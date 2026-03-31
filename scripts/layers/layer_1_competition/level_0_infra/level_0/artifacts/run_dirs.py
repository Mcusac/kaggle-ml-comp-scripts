"""Run directory helpers shared across contests."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

from layers.layer_0_core.level_0 import ensure_dir


def ensure_run_dir(run_dir: str | Path, *, subdirs: Optional[Iterable[str]] = None) -> Path:
    """
    Ensure a run directory exists, optionally creating common subdirectories.

    This does not impose a schema; contests can choose their own filenames/layout.
    """
    p = Path(run_dir)
    ensure_dir(p)
    for name in subdirs or ():
        ensure_dir(p / str(name))
    return p


__all__ = ["ensure_run_dir"]

