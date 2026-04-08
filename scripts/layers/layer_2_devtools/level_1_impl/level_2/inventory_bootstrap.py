#!/usr/bin/env python3
"""
Emit a machine-generated markdown fragment for the code-audit planner to merge
under a \"Machine-generated (verify)\" section of INVENTORY_<level>.md.

Run from scripts/:  python dev/scripts/inventory_bootstrap.py --level-path <dir> [--output path.md]
"""

import argparse
import io
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_SCRIPTS_ROOT = _SCRIPT_DIR.parents[3]
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_1.api_maintenance import (
    run_inventory_bootstrap_cli_api,
)


def _win_utf8_stdio() -> None:
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding="utf-8", errors="replace"
        )


def main() -> int:
    _win_utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--level-path", type=Path, required=True)
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=None,
        help="Optional workspace root for relative path line in output",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Write to file (default: print to stdout)",
    )
    args = parser.parse_args()
    env = run_inventory_bootstrap_cli_api(
        {
            "level_path": args.level_path,
            "workspace_root": args.workspace_root.resolve()
            if args.workspace_root
            else None,
            "output": args.output,
        }
    )
    if env["status"] != "ok":
        raise SystemExit("\n".join(env["errors"]))
    data = env["data"]
    if data["wrote_file"]:
        print(f"[OK] Wrote {data['output_path']}")
    else:
        print(data["body"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
