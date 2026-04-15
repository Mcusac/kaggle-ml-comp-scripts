import argparse
import sys
from pathlib import Path

# Go up to scripts/ root (6 levels up from this file)
_SCRIPTS = Path(__file__).resolve().parents[5]
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from layers.layer_2_devtools.level_1_impl.level_1 import (
    run_dump_level_preset_cli_api,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("level_name")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("package_dumps"),
        help="Directory for dump output (default: package_dumps)",
    )
    args = parser.parse_args()

    env = run_dump_level_preset_cli_api(
        {
            "level_name": args.level_name,
            "scripts_root": _SCRIPTS,
            "output_dir": args.output_dir,
        }
    )

    if env["status"] != "ok":
        print("\n".join(env["errors"]), file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())