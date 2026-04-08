"""
Apply import-layering fixes driven by level_violations_scan_*.json.

Order: DEEP_PATH (none expected) -> RELATIVE_IN_LOGIC -> WRONG_LEVEL.
UPWARD is report-only (no bundled auto-fix).

Default is --dry-run. Use --apply to modify files. Optionally --verify runs
general stack scan and writes JSON after fixes.
"""

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_SCRIPTS_ROOT = _SCRIPT_DIR.parent
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_1.api_violations import run_violation_fix_cli_api


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, default=None, help="Scan JSON path")
    parser.add_argument(
        "--audits-dir",
        type=Path,
        default=None,
        help="Folder containing level_violations_scan_*.json (default: workspace .cursor/.../audits)",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply bundled fixes (default is dry-run summary only)",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="After --apply, re-run general stack scan and write .md/.json",
    )
    args = parser.parse_args()
    scripts_dev = Path(__file__).resolve().parent
    env = run_violation_fix_cli_api(
        {
            "json_path": args.json,
            "audits_dir": args.audits_dir,
            "apply": bool(args.apply),
            "verify": bool(args.verify),
            "scripts_dev_dir": scripts_dev,
            "scripts_root": _SCRIPTS_ROOT,
        }
    )
    if env["status"] != "ok":
        raise SystemExit("\n".join(env["errors"]))


if __name__ == "__main__":
    main()
