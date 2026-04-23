"""Suggest promotion/demotion candidates based on inbound usage (report-only).

This module is intentionally "level_0" infra: pure computation + small models.
It does not touch the filesystem; callers provide precomputed module levels and
incoming dependency maps.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class UsageEvidence:
    importer_module: str
    importer_level: int

    def to_dict(self) -> dict:
        return {
            "importer_module": self.importer_module,
            "importer_level": int(self.importer_level),
        }


@dataclass(frozen=True)
class HeavyReusePolicy:
    """Heuristics to label a module as heavily reused."""

    min_total_inbound: int = 10
    min_distinct_importers: int = 5
    min_distinct_levels: int = 2


@dataclass(frozen=True)
class PromotionSuggestionRow:
    module: str
    current_level: int | None
    inbound_total: int
    inbound_by_level: dict[int, int]
    distinct_importer_levels: tuple[int, ...]
    heavy_reuse: bool
    suggested_level: int | None
    status: str  # ok | no_change | unknown | skipped
    top_importers: tuple[UsageEvidence, ...] = ()

    def to_dict(self) -> dict:
        return {
            "module": self.module,
            "current_level": self.current_level,
            "inbound_total": int(self.inbound_total),
            "inbound_by_level": {str(k): int(v) for k, v in sorted(self.inbound_by_level.items())},
            "distinct_importer_levels": [int(x) for x in self.distinct_importer_levels],
            "heavy_reuse": bool(self.heavy_reuse),
            "suggested_level": self.suggested_level,
            "status": self.status,
            "top_importers": [e.to_dict() for e in self.top_importers],
        }


@dataclass(frozen=True)
class DemotionSuggestionRow:
    module: str
    current_level: int | None
    inbound_total: int
    inbound_by_level: dict[int, int]
    distinct_importer_levels: tuple[int, ...]
    suggested_level: int | None
    status: str  # ok | no_change | unknown | skipped
    top_importers: tuple[UsageEvidence, ...] = ()

    def to_dict(self) -> dict:
        return {
            "module": self.module,
            "current_level": self.current_level,
            "inbound_total": int(self.inbound_total),
            "inbound_by_level": {str(k): int(v) for k, v in sorted(self.inbound_by_level.items())},
            "distinct_importer_levels": [int(x) for x in self.distinct_importer_levels],
            "suggested_level": self.suggested_level,
            "status": self.status,
            "top_importers": [e.to_dict() for e in self.top_importers],
        }


def suggest_promotions(
    *,
    modules: Iterable[str],
    module_level: Mapping[str, int | None],
    incoming: Mapping[str, Sequence[UsageEvidence]],
    policy: HeavyReusePolicy,
    top_importers_limit: int = 10,
) -> list[PromotionSuggestionRow]:
    """Suggest promotions (move to a higher level number) based on inbound usage.

    The recommendation is intentionally conservative and report-only.
    """
    out: list[PromotionSuggestionRow] = []
    for mod in sorted(set(modules)):
        cur = module_level.get(mod)
        evidence = tuple(incoming.get(mod, ()))
        inbound_total = len(evidence)
        by_level = _count_by_level(evidence)
        importer_levels = tuple(sorted(by_level.keys()))

        if cur is None:
            out.append(
                PromotionSuggestionRow(
                    module=mod,
                    current_level=None,
                    inbound_total=inbound_total,
                    inbound_by_level=by_level,
                    distinct_importer_levels=importer_levels,
                    heavy_reuse=False,
                    suggested_level=None,
                    status="unknown",
                    top_importers=_top_importers(evidence, limit=top_importers_limit),
                )
            )
            continue

        heavy_reuse = _is_heavy_reuse(
            inbound_total=inbound_total,
            distinct_importers=_distinct_importers(evidence),
            distinct_levels=len(importer_levels),
            policy=policy,
        )
        if not importer_levels:
            # No inbound usage within the scoped graph.
            out.append(
                PromotionSuggestionRow(
                    module=mod,
                    current_level=cur,
                    inbound_total=inbound_total,
                    inbound_by_level=by_level,
                    distinct_importer_levels=importer_levels,
                    heavy_reuse=heavy_reuse,
                    suggested_level=cur,
                    status="skipped",
                    top_importers=(),
                )
            )
            continue

        # Promotion means moving "up" numerically. Keep it bounded to avoid jumping too far:
        # - at most +1 from current level
        # - never to >= max(importer_level), so most importers stay above it
        max_importer = max(importer_levels)
        candidate = min(cur + 1, max_importer - 1)
        suggested: int | None = candidate if candidate > cur else cur

        status = "no_change"
        if heavy_reuse and suggested is not None and suggested != cur:
            status = "ok"
        out.append(
            PromotionSuggestionRow(
                module=mod,
                current_level=cur,
                inbound_total=inbound_total,
                inbound_by_level=by_level,
                distinct_importer_levels=importer_levels,
                heavy_reuse=heavy_reuse,
                suggested_level=suggested,
                status=status,
                top_importers=_top_importers(evidence, limit=top_importers_limit),
            )
        )
    return out


def suggest_demotions(
    *,
    modules: Iterable[str],
    module_level: Mapping[str, int | None],
    incoming: Mapping[str, Sequence[UsageEvidence]],
    top_importers_limit: int = 10,
) -> list[DemotionSuggestionRow]:
    """Suggest demotions (move to a lower level number) when only used by lower levels."""
    out: list[DemotionSuggestionRow] = []
    for mod in sorted(set(modules)):
        cur = module_level.get(mod)
        evidence = tuple(incoming.get(mod, ()))
        inbound_total = len(evidence)
        by_level = _count_by_level(evidence)
        importer_levels = tuple(sorted(by_level.keys()))

        if cur is None:
            out.append(
                DemotionSuggestionRow(
                    module=mod,
                    current_level=None,
                    inbound_total=inbound_total,
                    inbound_by_level=by_level,
                    distinct_importer_levels=importer_levels,
                    suggested_level=None,
                    status="unknown",
                    top_importers=_top_importers(evidence, limit=top_importers_limit),
                )
            )
            continue

        if not importer_levels:
            out.append(
                DemotionSuggestionRow(
                    module=mod,
                    current_level=cur,
                    inbound_total=inbound_total,
                    inbound_by_level=by_level,
                    distinct_importer_levels=importer_levels,
                    suggested_level=cur,
                    status="skipped",
                    top_importers=(),
                )
            )
            continue

        # Demotion candidate if all importers are strictly lower.
        if all(int(lvl) < int(cur) for lvl in importer_levels):
            max_importer = max(importer_levels)
            suggested = max(0, int(max_importer) + 1)
            if suggested < int(cur):
                status = "ok"
            else:
                suggested = cur
                status = "no_change"
        else:
            suggested = cur
            status = "no_change"

        out.append(
            DemotionSuggestionRow(
                module=mod,
                current_level=cur,
                inbound_total=inbound_total,
                inbound_by_level=by_level,
                distinct_importer_levels=importer_levels,
                suggested_level=suggested,
                status=status,
                top_importers=_top_importers(evidence, limit=top_importers_limit),
            )
        )
    return out


def _count_by_level(evidence: Sequence[UsageEvidence]) -> dict[int, int]:
    out: dict[int, int] = {}
    for e in evidence:
        out[int(e.importer_level)] = out.get(int(e.importer_level), 0) + 1
    return dict(sorted(out.items(), key=lambda kv: kv[0]))


def _distinct_importers(evidence: Sequence[UsageEvidence]) -> int:
    return len({e.importer_module for e in evidence})


def _is_heavy_reuse(
    *,
    inbound_total: int,
    distinct_importers: int,
    distinct_levels: int,
    policy: HeavyReusePolicy,
) -> bool:
    if inbound_total < int(policy.min_total_inbound):
        return False
    if distinct_importers < int(policy.min_distinct_importers):
        return False
    if distinct_levels < int(policy.min_distinct_levels):
        return False
    return True


def _top_importers(evidence: Sequence[UsageEvidence], *, limit: int) -> tuple[UsageEvidence, ...]:
    if limit <= 0:
        return ()
    # Prefer lower-level importers first for stability; then name.
    return tuple(sorted(evidence, key=lambda e: (e.importer_level, e.importer_module))[:limit])

