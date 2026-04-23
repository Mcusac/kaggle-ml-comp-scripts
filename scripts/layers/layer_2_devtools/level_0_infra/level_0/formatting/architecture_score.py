"""Compute a single numeric architecture score from existing devtool artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


def _as_dict(x: object) -> dict[str, Any]:
    return x if isinstance(x, dict) else {}


def _as_list(x: object) -> list[Any]:
    return x if isinstance(x, list) else []


def _safe_int(x: object, default: int = 0) -> int:
    try:
        return int(x)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class ScoreComponent:
    name: str
    points: int
    max_points: int
    rationale: str


@dataclass(frozen=True)
class ScoreResult:
    score: int
    max_score: int
    components: list[ScoreComponent]
    inputs: dict[str, Any]


@dataclass(frozen=True)
class ScoreConfig:
    max_score: int = 100

    # Health-derived penalties (defaults intentionally simple/stable)
    penalty_unused_imports_per_50: int = 1
    penalty_long_file_over_threshold: int = 1
    penalty_high_complexity_func: int = 1
    penalty_high_complexity_class: int = 1
    penalty_duplicate_lines_per_200: int = 1
    penalty_srp_violation_per_10: int = 1

    # Manifest-derived penalties
    penalty_manifest_failed_step: int = 10
    penalty_manifest_skipped_step: int = 3
    penalty_manifest_violation_bucket: int = 1  # per 10 violations in step metrics

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "ScoreConfig":
        d = _as_dict(data)
        return ScoreConfig(
            max_score=_safe_int(d.get("max_score"), 100),
            penalty_unused_imports_per_50=_safe_int(d.get("penalty_unused_imports_per_50"), 1),
            penalty_long_file_over_threshold=_safe_int(d.get("penalty_long_file_over_threshold"), 1),
            penalty_high_complexity_func=_safe_int(d.get("penalty_high_complexity_func"), 1),
            penalty_high_complexity_class=_safe_int(d.get("penalty_high_complexity_class"), 1),
            penalty_duplicate_lines_per_200=_safe_int(d.get("penalty_duplicate_lines_per_200"), 1),
            penalty_srp_violation_per_10=_safe_int(d.get("penalty_srp_violation_per_10"), 1),
            penalty_manifest_failed_step=_safe_int(d.get("penalty_manifest_failed_step"), 10),
            penalty_manifest_skipped_step=_safe_int(d.get("penalty_manifest_skipped_step"), 3),
            penalty_manifest_violation_bucket=_safe_int(d.get("penalty_manifest_violation_bucket"), 1),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "max_score": int(self.max_score),
            "penalty_unused_imports_per_50": int(self.penalty_unused_imports_per_50),
            "penalty_long_file_over_threshold": int(self.penalty_long_file_over_threshold),
            "penalty_high_complexity_func": int(self.penalty_high_complexity_func),
            "penalty_high_complexity_class": int(self.penalty_high_complexity_class),
            "penalty_duplicate_lines_per_200": int(self.penalty_duplicate_lines_per_200),
            "penalty_srp_violation_per_10": int(self.penalty_srp_violation_per_10),
            "penalty_manifest_failed_step": int(self.penalty_manifest_failed_step),
            "penalty_manifest_skipped_step": int(self.penalty_manifest_skipped_step),
            "penalty_manifest_violation_bucket": int(self.penalty_manifest_violation_bucket),
        }


def load_score_config_optional(path: Path | None) -> ScoreConfig:
    """Load an optional score config JSON file (missing/unreadable => defaults)."""
    if path is None:
        return ScoreConfig()
    p = Path(path)
    if not p.is_file():
        return ScoreConfig()
    try:
        import json

        with open(p, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return ScoreConfig()
        return ScoreConfig.from_dict(data)
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return ScoreConfig()


def _penalty_units(count: int, per: int) -> int:
    if per <= 0:
        return 0
    if count <= 0:
        return 0
    return (count + per - 1) // per


def compute_health_score(health: dict[str, Any], config: ScoreConfig) -> tuple[int, list[ScoreComponent], dict[str, Any]]:
    h = _as_dict(health)
    comp: list[ScoreComponent] = []
    penalties = 0

    dead = _as_dict(h.get("dead_code"))
    unused_imports = _safe_int(dead.get("total_unused_imports"), 0)
    p_unused = _penalty_units(unused_imports, 50) * config.penalty_unused_imports_per_50
    penalties += p_unused
    comp.append(
        ScoreComponent(
            name="unused_imports",
            points=-p_unused,
            max_points=0,
            rationale=f"total_unused_imports={unused_imports}",
        )
    )

    fm = _as_dict(h.get("file_metrics"))
    long_files = _as_list(fm.get("long_files"))
    oversized_count = 0
    for row in long_files:
        r = _as_dict(row)
        if _safe_int(r.get("lines"), 0) > 0:
            oversized_count += 1
    p_oversized = oversized_count * config.penalty_long_file_over_threshold
    penalties += p_oversized
    comp.append(
        ScoreComponent(
            name="oversized_modules",
            points=-p_oversized,
            max_points=0,
            rationale=f"long_files={oversized_count}",
        )
    )

    cx = _as_dict(h.get("complexity"))
    funcs = _as_list(cx.get("functions"))
    classes = _as_list(cx.get("classes"))
    high_funcs = 0
    for f in funcs:
        row = _as_dict(f)
        if _safe_int(row.get("complexity"), 0) >= 20:
            high_funcs += 1
    high_classes = 0
    for c in classes:
        row = _as_dict(c)
        if _safe_int(row.get("complexity"), 0) >= 50:
            high_classes += 1
    p_hf = high_funcs * config.penalty_high_complexity_func
    p_hc = high_classes * config.penalty_high_complexity_class
    penalties += p_hf + p_hc
    comp.append(
        ScoreComponent(
            name="high_complexity",
            points=-(p_hf + p_hc),
            max_points=0,
            rationale=f"high_funcs(>=20)={high_funcs}, high_classes(>=50)={high_classes}",
        )
    )

    dup = _as_dict(h.get("duplication"))
    dup_lines = _safe_int(
        dup.get("total_duplicate_lines") or dup.get("duplicate_lines"),
        0,
    )
    p_dup = _penalty_units(dup_lines, 200) * config.penalty_duplicate_lines_per_200
    penalties += p_dup
    comp.append(
        ScoreComponent(
            name="duplication",
            points=-p_dup,
            max_points=0,
            rationale=f"duplicate_lines={dup_lines}",
        )
    )

    solid = _as_dict(h.get("solid"))
    srp = _as_list(solid.get("srp_violations"))
    srp_count = len(srp)
    p_srp = _penalty_units(srp_count, 10) * config.penalty_srp_violation_per_10
    penalties += p_srp
    comp.append(
        ScoreComponent(
            name="srp_violations",
            points=-p_srp,
            max_points=0,
            rationale=f"srp_violations={srp_count}",
        )
    )

    inputs = {
        "unused_imports": unused_imports,
        "oversized_count": oversized_count,
        "high_complexity_functions": high_funcs,
        "high_complexity_classes": high_classes,
        "duplicate_lines": dup_lines,
        "srp_violations": srp_count,
    }
    score = max(0, int(config.max_score) - int(penalties))
    return score, comp, inputs


def compute_manifest_score(manifest: dict[str, Any], config: ScoreConfig) -> tuple[int, list[ScoreComponent], dict[str, Any]]:
    m = _as_dict(manifest)
    comp: list[ScoreComponent] = []
    penalties = 0

    steps = m.get("steps")
    steps_d = steps if isinstance(steps, dict) else {}
    failed_steps = _as_list(_as_dict(m.get("aggregate")).get("failed_steps"))
    skipped_steps = _as_list(_as_dict(m.get("aggregate")).get("skipped_steps"))

    p_failed = len(failed_steps) * config.penalty_manifest_failed_step
    p_skipped = len(skipped_steps) * config.penalty_manifest_skipped_step
    penalties += p_failed + p_skipped
    comp.append(
        ScoreComponent(
            name="manifest_step_outcomes",
            points=-(p_failed + p_skipped),
            max_points=0,
            rationale=f"failed_steps={len(failed_steps)}, skipped_steps={len(skipped_steps)}",
        )
    )

    # Look for common violation_count metrics by step.
    total_violation_count = 0
    for _, rec in steps_d.items():
        r = _as_dict(rec)
        metrics = _as_dict(r.get("metrics"))
        total_violation_count += _safe_int(metrics.get("violation_count"), 0)
        total_violation_count += _safe_int(metrics.get("cycle_count"), 0)
        total_violation_count += _safe_int(metrics.get("unreferenced_count"), 0)
        total_violation_count += _safe_int(metrics.get("unreachable_count"), 0)

    p_v = _penalty_units(total_violation_count, 10) * config.penalty_manifest_violation_bucket
    penalties += p_v
    comp.append(
        ScoreComponent(
            name="manifest_violation_buckets",
            points=-p_v,
            max_points=0,
            rationale=f"aggregated_violation_like_count={total_violation_count}",
        )
    )

    inputs = {
        "failed_steps": len(failed_steps),
        "skipped_steps": len(skipped_steps),
        "aggregated_violation_like_count": total_violation_count,
    }
    score = max(0, int(config.max_score) - int(penalties))
    return score, comp, inputs


def compute_architecture_score(
    *,
    health: dict[str, Any] | None = None,
    manifest: dict[str, Any] | None = None,
    config: ScoreConfig | None = None,
) -> ScoreResult:
    cfg = config or ScoreConfig()
    components: list[ScoreComponent] = []
    inputs: dict[str, Any] = {}

    # Start at max and subtract combined penalties by composing components.
    score = int(cfg.max_score)

    if health is not None:
        s, comps, inp = compute_health_score(health, cfg)
        # Convert to penalty delta from max.
        score -= int(cfg.max_score) - int(s)
        components.extend(comps)
        inputs["health"] = inp

    if manifest is not None:
        s, comps, inp = compute_manifest_score(manifest, cfg)
        score -= int(cfg.max_score) - int(s)
        components.extend(comps)
        inputs["manifest"] = inp

    final = max(0, min(int(cfg.max_score), int(score)))
    return ScoreResult(
        score=final,
        max_score=int(cfg.max_score),
        components=components,
        inputs=inputs,
    )

