"""Package tree dump CLI — entrypoint only; logic in devtools layer."""

import sys
from pathlib import Path

_FW_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_FW_ROOT) not in sys.path:
    sys.path.insert(0, str(_FW_ROOT))

from layers.layer_2_devtools.level_1_impl.level_1.api_maintenance import (
    run_package_dump_sys_argv_api,
)


def main() -> int:
    env = run_package_dump_sys_argv_api(sys.argv[1:])
    if env["status"] != "ok":
        print("\n".join(env["errors"]), file=sys.stderr)
        return 1
    return int(env["data"]["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
