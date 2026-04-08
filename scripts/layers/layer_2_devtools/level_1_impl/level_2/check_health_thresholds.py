#!/usr/bin/env python3
"""
Package Health Threshold Checker

Enforces code quality thresholds based on check_health.py JSON output.

Exit codes:
- 0: All checks passed (or passed with warnings when not --strict)
- 1: Fatal violations
- 2: Warnings only (strict mode)

Usage:
  From project root:  python scripts/dev/scripts/check_health_thresholds.py <report.json> [--config FILE] [--strict]
  From scripts/:      python dev/scripts/check_health_thresholds.py <report.json> [--config FILE] [--strict]
"""

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_SCRIPTS_ROOT = _SCRIPT_DIR.parent.parent
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_1.api_health import run_health_threshold_check_api


def main() -> int:
    """Main entry point for threshold checking."""
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding="utf-8", errors="replace"
        )

    parser = argparse.ArgumentParser(
        description="Check package health thresholds",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "report_file",
        type=Path,
        help="Path to check_health.py JSON output",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Threshold configuration file (JSON)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat warnings as failures",
    )

    args = parser.parse_args()

    env = run_health_threshold_check_api(
        {
            "report_file": args.report_file,
            "threshold_config_path": args.config,
            "strict": args.strict,
        }
    )
    if env["status"] != "ok":
        print(f"❌ Error: {'; '.join(env['errors'])}")
        return 1
    return int(env["data"]["exit_code"])


if __name__ == "__main__":
    sys.exit(main())
