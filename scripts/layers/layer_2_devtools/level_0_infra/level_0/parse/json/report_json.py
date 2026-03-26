"""Atomic JSON report loading utilities for devtools scripts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json_report(path: Path) -> dict[str, Any]:
    """Load report JSON with UTF fallback and leading-text stripping."""
    if not path.exists():
        raise FileNotFoundError(str(path))
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        content = path.read_text(encoding="utf-16")
    if content.startswith("\ufeff"):
        content = content[1:]
    json_start = content.find("{")
    if json_start == -1:
        raise ValueError(f"No JSON object found in report: {path}")
    if json_start > 0:
        content = content[json_start:]
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to parse JSON report {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object at top level in {path}, got {type(data)}")
    return data


__all__ = ["load_json_report"]
