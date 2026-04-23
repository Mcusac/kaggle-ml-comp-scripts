#!/usr/bin/env python3
"""Thin wrapper; canonical: ``python layers/layer_2_devtools/level_1_impl/level_2/package_boundary_validator.py``."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_HERE = Path(__file__).resolve()
_SCRIPTS = _HERE.parents[3]
_TARGET = (
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_1_impl"
    / "level_2"
    / "package_boundary_validator.py"
)


def _load(path: Path):
    spec = importlib.util.spec_from_file_location("_package_boundary_validator_entry", str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


main = _load(_TARGET).main

if __name__ == "__main__":
    raise SystemExit(main())

