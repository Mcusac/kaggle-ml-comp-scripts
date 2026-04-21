#!/usr/bin/env python3
"""
Summarize duplication findings from a check_health JSON report.

Usage:
  From scripts/: python -m layers.layer_2_devtools.level_1_impl.level_2.report_duplicates path/to/health_report.json
"""

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
        description="Summarize duplication findings from a health report.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("report", type=Path, help="Path to health_report.json")
    parser.add_argument(
        "--top", type=int, default=20, help="Show top N largest duplicate blocks"
    )
    args = parser.parse_args()

    env = emit_health_report_view_api(
        {
            "view_kind": "duplicates",
            "report_path": args.report,
            "top": args.top,
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
