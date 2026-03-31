"""JSON artifact read/write utilities (format-preserving, infra-level)."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any

from layers.layer_0_core.level_0 import ensure_dir


def read_json(path: str | Path) -> Any:
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
    p = Path(path)
    ensure_dir(p.parent)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=int(indent), ensure_ascii=bool(ensure_ascii))


def write_json_atomic(
    path: str | Path,
    data: Any,
    *,
    indent: int = 2,
    ensure_ascii: bool = False,
) -> None:
    """
    Atomically write JSON by writing to a temp file in the same directory then replacing.
    Preserves file format knobs via indent/ensure_ascii.
    """
    p = Path(path)
    ensure_dir(p.parent)
    tmp_fd = None
    tmp_path = None
    try:
        tmp_fd, tmp_path = tempfile.mkstemp(
            prefix=p.name + ".",
            suffix=".tmp",
            dir=str(p.parent),
        )
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            tmp_fd = None
            json.dump(data, f, indent=int(indent), ensure_ascii=bool(ensure_ascii))
        os.replace(str(tmp_path), str(p))
    finally:
        if tmp_fd is not None:
            try:
                os.close(tmp_fd)
            except Exception:
                pass
        if tmp_path is not None:
            try:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
            except Exception:
                pass


__all__ = ["read_json", "write_json", "write_json_atomic"]

