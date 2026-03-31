"""Generic JSON read/write helpers for contest/infra code."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from layers.layer_0_core.level_0 import ensure_dir


def read_json(path: str | Path) -> Any:
    """Read JSON from `path` and return the parsed object."""
    p = Path(path)
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(
    path: str | Path,
    data: Any,
    *,
    indent: int = 2,
    ensure_ascii: bool = False,
) -> None:
    """Write `data` as JSON to `path`, creating parent directories."""
    p = Path(path)
    ensure_dir(p.parent)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=int(indent), ensure_ascii=bool(ensure_ascii))

