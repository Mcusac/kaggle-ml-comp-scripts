"""Best-config artifact helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from layers.layer_1_competition.level_0_infra.level_0.artifacts.json_artifacts import (
    read_json,
)


def load_best_config_json(path: Path, *, drop_key: str | None = "score") -> dict[str, Any]:
    """Load a best-config JSON file and optionally drop a bookkeeping key."""
    payload = read_json(path)
    if not isinstance(payload, dict):
        raise TypeError(f"Expected best config JSON object at {path}, got {type(payload).__name__}")
    result = dict(payload)
    if drop_key:
        result.pop(drop_key, None)
    return result

