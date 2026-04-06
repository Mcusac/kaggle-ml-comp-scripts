"""Generic JSON read/write helpers for contest/infra code."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from layers.layer_1_competition.level_0_infra.level_0.artifacts.json_artifacts import (
    read_json as _read_json,
    write_json as _write_json,
)


def read_json(path: str | Path) -> Any:
    """Read JSON from `path` and return the parsed object."""
    return _read_json(path)


def write_json(
    path: str | Path,
    data: Any,
    *,
    indent: int = 2,
    ensure_ascii: bool = False,
) -> None:
    """Write `data` as JSON to `path`, creating parent directories."""
    _write_json(path, data, indent=indent, ensure_ascii=ensure_ascii)

