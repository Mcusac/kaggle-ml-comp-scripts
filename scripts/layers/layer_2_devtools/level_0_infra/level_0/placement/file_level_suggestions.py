"""Compute minimal valid file levels (report-only).

This module is intentionally "level_0" infra: pure computation + small models.
It does not touch the filesystem besides receiving precomputed inputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class Evidence:
    """One driver for a constraint (incoming or outgoing)."""

    module: str
    referenced: str
    referenced_level: int

    def to_dict(self) -> dict:
        return {
            "module": self.module,
            "referenced": self.referenced,
            "referenced_level": int(self.referenced_level),
        }


@dataclass(frozen=True)
class FileLevelSuggestionRow:
    module: str
    current_level: int | None
    lb_required: int | None
    ub_allowed: int | None
    suggested_level: int | None
    status: str  # ok | conflict | unknown | no_change
    outgoing_drivers: tuple[Evidence, ...] = ()
    incoming_drivers: tuple[Evidence, ...] = ()

    def to_dict(self) -> dict:
        return {
            "module": self.module,
            "current_level": self.current_level,
            "lb_required": self.lb_required,
            "ub_allowed": self.ub_allowed,
            "suggested_level": self.suggested_level,
            "status": self.status,
            "outgoing_drivers": [e.to_dict() for e in self.outgoing_drivers],
            "incoming_drivers": [e.to_dict() for e in self.incoming_drivers],
        }


@dataclass(frozen=True)
class LevelPolicy:
    """Scope-specific tiering rules.

    For a source module at level K importing a referenced module at level J:
    - if `min_level_delta_for_outgoing` is 1, then K must be >= J+1.
    - if it is 0, then K must be >= J (same-tier allowed).

    For incoming constraints (an importer at level K importing this module),
    the maximum allowed level for this module is:
    - if `max_level_delta_for_incoming` is -1, then this module must be <= K-1.
    - if it is 0, then this module may be <= K.
    """

    min_level_delta_for_outgoing: int
    max_level_delta_for_incoming: int


def suggest_levels(
    *,
    modules: Iterable[str],
    module_level: Mapping[str, int | None],
    outgoing_level_refs: Mapping[str, Sequence[Evidence]],
    incoming_level_refs: Mapping[str, Sequence[Evidence]],
    policy: LevelPolicy,
) -> list[FileLevelSuggestionRow]:
    """Compute per-module minimal valid level suggestions.

    Inputs are pre-normalized:
    - `outgoing_level_refs[module]` contains only references that belong to the scope
      and have a resolvable referenced_level.
    - `incoming_level_refs[module]` contains importer evidence similarly normalized.
    """

    out: list[FileLevelSuggestionRow] = []
    for mod in sorted(set(modules)):
        cur = module_level.get(mod)
        outgoing = tuple(outgoing_level_refs.get(mod, ()))
        incoming = tuple(incoming_level_refs.get(mod, ()))

        lb: int | None
        if outgoing:
            lb = max(e.referenced_level + policy.min_level_delta_for_outgoing for e in outgoing)
        else:
            lb = None

        ub: int | None
        if incoming:
            ub = min(e.referenced_level + policy.max_level_delta_for_incoming for e in incoming)
        else:
            ub = None

        # Unknown: no level for file (e.g., outside tiered dirs), and no constraints.
        if cur is None and lb is None and ub is None:
            out.append(
                FileLevelSuggestionRow(
                    module=mod,
                    current_level=None,
                    lb_required=None,
                    ub_allowed=None,
                    suggested_level=None,
                    status="unknown",
                )
            )
            continue

        # Conflicts only meaningful when both bounds known.
        if lb is not None and ub is not None and lb > ub:
            out.append(
                FileLevelSuggestionRow(
                    module=mod,
                    current_level=cur,
                    lb_required=lb,
                    ub_allowed=ub,
                    suggested_level=None,
                    status="conflict",
                    outgoing_drivers=_top_level_drivers(outgoing, target=lb, delta=policy.min_level_delta_for_outgoing),
                    incoming_drivers=_top_level_drivers_incoming(incoming, target=ub, delta=policy.max_level_delta_for_incoming),
                )
            )
            continue

        # Choose target: at least current and lb; also must not exceed ub.
        target = cur if cur is not None else lb
        if lb is not None:
            target = max(target or lb, lb) if target is not None else lb
        if ub is not None and target is not None:
            target = min(target, ub)

        if target is None:
            out.append(
                FileLevelSuggestionRow(
                    module=mod,
                    current_level=cur,
                    lb_required=lb,
                    ub_allowed=ub,
                    suggested_level=None,
                    status="unknown",
                    outgoing_drivers=outgoing,
                    incoming_drivers=incoming,
                )
            )
            continue

        status = "ok"
        if cur is not None and target == cur:
            status = "no_change"

        out.append(
            FileLevelSuggestionRow(
                module=mod,
                current_level=cur,
                lb_required=lb,
                ub_allowed=ub,
                suggested_level=target,
                status=status,
                outgoing_drivers=_top_level_drivers(outgoing, target=lb, delta=policy.min_level_delta_for_outgoing),
                incoming_drivers=_top_level_drivers_incoming(incoming, target=ub, delta=policy.max_level_delta_for_incoming),
            )
        )
    return out


def _top_level_drivers(
    evidence: Sequence[Evidence],
    *,
    target: int | None,
    delta: int,
) -> tuple[Evidence, ...]:
    if target is None:
        return tuple(evidence)
    # Keep only drivers that hit the max LB.
    drivers = [e for e in evidence if (e.referenced_level + delta) == target]
    return tuple(sorted(drivers, key=lambda e: (e.referenced_level, e.referenced, e.module)))


def _top_level_drivers_incoming(
    evidence: Sequence[Evidence],
    *,
    target: int | None,
    delta: int,
) -> tuple[Evidence, ...]:
    if target is None:
        return tuple(evidence)
    # For UB, driver minimizes referenced_level + delta.
    drivers = [e for e in evidence if (e.referenced_level + delta) == target]
    return tuple(sorted(drivers, key=lambda e: (e.referenced_level, e.referenced, e.module)))

