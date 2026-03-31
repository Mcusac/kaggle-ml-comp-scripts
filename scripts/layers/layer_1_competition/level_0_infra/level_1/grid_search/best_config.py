"""Helpers for loading best-config style JSON artifacts."""

from pathlib import Path
from typing import Any, Iterable

from layers.layer_1_competition.level_0_infra.level_0 import read_json


def load_best_config_json(
    path: str | Path,
    *,
    drop_keys: Iterable[str] = ("_tune_score", "_tune_search_type"),
) -> dict[str, Any]:
    """
    Load a best_config.json-like file as a dict and drop known metadata keys.

    This is intentionally schema-agnostic; contests may interpret the dict.
    """
    obj = read_json(path)
    if not isinstance(obj, dict):
        raise ValueError(f"Best config must be a JSON object/dict, got {type(obj).__name__}")
    out = dict(obj)
    for k in drop_keys:
        out.pop(str(k), None)
    return out


__all__ = ["load_best_config_json"]

