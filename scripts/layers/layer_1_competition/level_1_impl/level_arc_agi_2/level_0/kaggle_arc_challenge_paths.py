"""Default Kaggle ARC-AGI-2 JSON paths (stdlib; respects ``KAGGLE_IS_COMPETITION_RERUN``)."""

from __future__ import annotations

import os

_DEFAULT_ROOT = "/kaggle/input/competitions/arc-prize-2026-arc-agi-2"


def _truthy_env(name: str) -> bool:
    v = os.getenv(name)
    if v is None:
        return False
    return str(v).strip().lower() in ("1", "true", "yes", "on")


def arc_kaggle_default_challenge_bundle_root() -> str:
    """Return default competition input root (override with env for local runs if needed)."""
    return str(os.getenv("ARC_KAGGLE_COMPETITION_ROOT", _DEFAULT_ROOT)).rstrip("/")


def arc_kaggle_challenges_json_path(*, bundle_root: str | None = None) -> str:
    """Evaluation vs test challenges path, mirroring reference notebook ``KAGGLE_IS_COMPETITION_RERUN``."""
    root = bundle_root or arc_kaggle_default_challenge_bundle_root()
    if _truthy_env("KAGGLE_IS_COMPETITION_RERUN"):
        return f"{root}/arc-agi_test_challenges.json"
    return f"{root}/arc-agi_evaluation_challenges.json"


def arc_kaggle_evaluation_solutions_json_path(*, bundle_root: str | None = None) -> str:
    """Public evaluation solutions (only valid when not in competition rerun mode)."""
    root = bundle_root or arc_kaggle_default_challenge_bundle_root()
    return f"{root}/arc-agi_evaluation_solutions.json"
