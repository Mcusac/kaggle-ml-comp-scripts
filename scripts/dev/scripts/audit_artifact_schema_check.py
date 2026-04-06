#!/usr/bin/env python3
"""Compatibility wrapper for level_2 devtools audit artifact schema checker."""

import runpy
import sys
from pathlib import Path

_SCRIPTS_ROOT = Path(__file__).resolve().parents[2]
_TARGET = (
    _SCRIPTS_ROOT
    / "layers"
    / "layer_2_devtools"
    / "level_1_impl"
    / "level_2"
    / "audit_artifact_schema_check.py"
)

if __name__ == "__main__":
    sys.path.insert(0, str(_SCRIPTS_ROOT))
    runpy.run_path(str(_TARGET), run_name="__main__")
