"""CLI entry for layer_0_core import rewrites — logic in devtools layer."""

import sys
from pathlib import Path

_SCRIPTS_ROOT = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_1.api_maintenance import (
    run_layer_core_import_rewrite_cli_api,
)


def main() -> int:
    env = run_layer_core_import_rewrite_cli_api({"scripts_root": _SCRIPTS_ROOT})
    if env["status"] != "ok":
        print("\n".join(env["errors"]), file=sys.stderr)
        return 1
    return int(env["data"]["exit_code"])


if __name__ == "__main__":
    sys.exit(main())
