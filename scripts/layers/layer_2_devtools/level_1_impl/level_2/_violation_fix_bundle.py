"""CLI entry for bundled RELATIVE_IN_LOGIC fixes — logic in devtools layer."""

import argparse
import sys
from pathlib import Path

_SCRIPTS_ROOT = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_1.api_maintenance import (
    run_violation_fix_bundle_standalone_cli_api,
)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--apply", action="store_true")
    args = p.parse_args()
    env = run_violation_fix_bundle_standalone_cli_api(
        {
            "scripts_dev_dir": Path(__file__).resolve().parent,
            "apply": args.apply,
        }
    )
    if env["status"] != "ok":
        raise SystemExit("\n".join(env["errors"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
