#!/usr/bin/env python3
"""
Remove __pycache__ directories and optional .pyc files under a root.

Usage:
  From scripts/:      python dev/scripts/clean_pycache.py [--root .] [--dry-run] [--pyc]
  From project root: python scripts/dev/scripts/clean_pycache.py [--root scripts] [--dry-run] [--pyc]
"""

import argparse
import io
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_SCRIPTS_ROOT = _SCRIPT_DIR.parent.parent
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_1.api_maintenance import run_clean_pycache_cli_api


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
        description="Remove __pycache__ directories and optional .pyc files under a root.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Root directory to scan")
    parser.add_argument("--dry-run", action="store_true", help="Only report what would be removed")
    parser.add_argument("--pyc", action="store_true", help="Also remove loose .pyc files")
    args = parser.parse_args()
    env = run_clean_pycache_cli_api(
        {
            "root": args.root,
            "dry_run": args.dry_run,
            "remove_pyc_files": args.pyc,
        }
    )
    if env["status"] != "ok":
        print(f"❌ Error: {'; '.join(env['errors'])}")
        return 1
    print(env["data"]["message"])
    return int(env["data"]["exit_code"])


if __name__ == "__main__":
    sys.exit(main())
