"""Boundary specification (allowed/disallowed edges) for package boundaries."""

from __future__ import annotations

from dataclasses import dataclass

from .boundary_classifiers import BoundaryClassifyResult


@dataclass(frozen=True)
class BoundaryDecision:
    allowed: bool
    violation_type: str | None
    reason: str | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "allowed": bool(self.allowed),
            "violation_type": self.violation_type,
            "reason": self.reason,
        }


def _devtools_rank(kind: str, level: int | None) -> int | None:
    if kind == "devtools_infra" and level is not None:
        return 100 + level
    if kind == "devtools_impl" and level is not None:
        return 200 + level
    if kind == "dev_scripts":
        return 1000
    return None


class PackageBoundarySpec:
    """Evaluate whether a boundary edge is allowed.

    This spec is intentionally small and focuses on *structural boundaries*:
    - Numeric tiers within the same stack (general stack, competition infra, each contest)
    - Devtools infra/impl/dev layering and disallowed external layers for devtools infra
    """

    def decide(self, *, source: BoundaryClassifyResult, target: BoundaryClassifyResult, target_module: str) -> BoundaryDecision:
        # Out-of-scope targets or sources are not boundary violations for this tool.
        if source.node is None or target.node is None:
            return BoundaryDecision(allowed=True, violation_type=None, reason="out_of_scope")

        # General stack: forbid upward (same-level is allowed at boundary level; surface rules handle same-level file placement).
        if source.node_kind == "general" and target.node_kind == "general":
            if source.level is not None and target.level is not None and target.level > source.level:
                return BoundaryDecision(
                    allowed=False,
                    violation_type="upward",
                    reason="upward_general_stack",
                )
            return BoundaryDecision(allowed=True, violation_type=None)

        # Competition infra: forbid upward within infra.
        if source.node_kind == "competition_infra" and target.node_kind == "competition_infra":
            if source.level is not None and target.level is not None and target.level > source.level:
                return BoundaryDecision(
                    allowed=False,
                    violation_type="upward",
                    reason="upward_competition_infra",
                )
            return BoundaryDecision(allowed=True, violation_type=None)

        # Contest tiers: forbid upward within the same contest slug.
        if source.node_kind == "contest" and target.node_kind == "contest":
            if source.contest_slug == target.contest_slug:
                if source.level is not None and target.level is not None and target.level > source.level:
                    return BoundaryDecision(
                        allowed=False,
                        violation_type="upward",
                        reason="upward_contest_tier",
                    )
                return BoundaryDecision(allowed=True, violation_type=None)
            # Cross-contest imports are treated as illegal external boundary for now.
            return BoundaryDecision(
                allowed=False,
                violation_type="illegal_external",
                reason="cross_contest_import",
            )

        # Devtools layering: infra < impl < dev scripts.
        s_rank = _devtools_rank(source.node_kind, source.level)
        t_rank = _devtools_rank(target.node_kind, target.level)
        if s_rank is not None and t_rank is not None:
            if t_rank > s_rank:
                return BoundaryDecision(
                    allowed=False,
                    violation_type="upward",
                    reason="upward_devtools_layering",
                )
            return BoundaryDecision(allowed=True, violation_type=None)

        # Devtools infra external layer restriction (mirrors dependency_validation_ops).
        if source.node_kind in ("devtools_infra",) and target_module.startswith("layers."):
            if target_module.startswith("layers.layer_0_core"):
                return BoundaryDecision(allowed=True, violation_type=None)
            if target_module.startswith("layers.layer_2_devtools.level_0_infra"):
                return BoundaryDecision(allowed=True, violation_type=None)
            return BoundaryDecision(
                allowed=False,
                violation_type="illegal_external",
                reason="devtools_infra_disallowed_layers_target",
            )

        # Other cross-boundary edges are allowed by default (policy can be tightened later).
        return BoundaryDecision(allowed=True, violation_type=None)

