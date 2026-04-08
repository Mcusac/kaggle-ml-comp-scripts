#!/usr/bin/env python3
"""
Remove unused imports from Python files based on package health report.

Usage:
  python dev/scripts/cleanup_imports.py --report unused_imports_report.json --dry-run
  python dev/scripts/cleanup_imports.py --report unused_imports_report.json
"""

import argparse
import io
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_SCRIPTS_ROOT = _SCRIPT_DIR.parent.parent
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_1.api_maintenance import (
    run_unused_import_cleanup_cli_api,
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
    parser = argparse.ArgumentParser(
        description="Remove unused imports from Python files based on health report."
    )
    parser.add_argument(
        "--report",
        type=Path,
        required=True,
        help="Path to health report JSON file",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Root directory for files (default: current directory)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be removed without actually modifying files",
    )
    args = parser.parse_args()
    env = run_unused_import_cleanup_cli_api(
        {
            "report": args.report,
            "root": args.root,
            "dry_run": args.dry_run,
        }
    )
    if env["status"] != "ok":
        print("\n".join(env["errors"]), file=sys.stderr)
        return 1
    return int(env["data"]["exit_code"])


if __name__ == "__main__":
    sys.exit(main())
