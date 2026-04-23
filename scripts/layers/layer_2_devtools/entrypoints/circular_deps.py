#!/usr/bin/env python3
"""Thin wrapper; canonical: ``python -m ...level_2.circular_deps``."""

from __future__ import annotations

import sys
from pathlib import Path
import importlib.util

_HERE = Path(__file__).resolve()
_SCRIPTS = _HERE.parents[2]

_TARGET = (
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_1_impl"
    / "level_2"
    / "circular_deps.py"
)


def _load(path: Path):
    spec = importlib.util.spec_from_file_location("_circular_deps_entry", str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


main = _load(_TARGET).main

if __name__ == "__main__":
    raise SystemExit(main())

