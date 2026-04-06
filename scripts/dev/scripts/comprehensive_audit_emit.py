#!/usr/bin/env python3
"""Compatibility wrapper for level_2 devtools comprehensive_audit_emit."""

import sys
from pathlib import Path

_SCRIPTS_ROOT = Path(__file__).resolve().parents[2]
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_2.comprehensive_audit_emit import main


if __name__ == "__main__":
    raise SystemExit(main())
