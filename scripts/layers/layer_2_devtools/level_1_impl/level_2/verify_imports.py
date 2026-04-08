"""
Import verification script.

Verifies all imports in the codebase are valid and can be resolved.
"""

import sys
from pathlib import Path

_SCRIPTS_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_1.api_maintenance import (
    run_verify_imports_stub_api,
)


def main() -> int:
    env = run_verify_imports_stub_api({})
    if env["status"] != "ok":
        print("\n".join(env["errors"]), file=sys.stderr)
        return 1
    for line in env["data"]["lines"]:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
