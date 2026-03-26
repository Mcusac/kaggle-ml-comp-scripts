"""Bootstrap ``sys.path`` for imports from the ``scripts`` tree."""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS_ROOT = Path(__file__).resolve().parents[4]
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from path_bootstrap import prepend_framework_paths

prepend_framework_paths()
