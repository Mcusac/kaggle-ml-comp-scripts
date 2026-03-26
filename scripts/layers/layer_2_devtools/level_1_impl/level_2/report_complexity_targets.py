#!/usr/bin/env python3
"""
Report current complexity for a small set of named targets from a check_health report.

Usage:
  From scripts/: python dev/scripts/report_complexity_targets.py path/to/health_report.json
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_SCRIPTS_ROOT = _SCRIPT_DIR.parent.parent
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_1.api_health import emit_health_report_view_api


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Report complexity for selected targets.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("report", type=Path, help="Path to health_report.json")
    parser.add_argument(
        "--targets",
        nargs="*",
        default=None,
        help="Class name substrings (omit for default named targets)",
    )
    args = parser.parse_args()

    env = emit_health_report_view_api(
        {
            "view_kind": "complexity",
            "report_path": args.report,
            "targets": list(args.targets) if args.targets else None,
        }
    )
    if env["status"] != "ok":
        print("\n".join(env["errors"]), file=sys.stderr)
        return 1
    for line in env["data"]["lines"]:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
