#!/usr/bin/env python3
"""Thin wrapper; canonical: ``python -m ...level_2.inventory_bootstrap``."""

import sys
from pathlib import Path

_SCRIPTS_ROOT = Path(__file__).resolve().parents[3]
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_2.inventory_bootstrap import main


if __name__ == "__main__":
    raise SystemExit(main())
