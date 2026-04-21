#!/usr/bin/env python3
"""
Compare two check_health JSON reports and print key deltas.

Usage:
  From scripts/: python -m layers.layer_2_devtools.level_1_impl.level_2.report_compare_health pre.json post.json
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
        description="Compare two health reports.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("pre", type=Path, help="Pre-change health report JSON")
    parser.add_argument("post", type=Path, help="Post-change health report JSON")
    args = parser.parse_args()

    env = emit_health_report_view_api(
        {
            "view_kind": "compare",
            "pre_path": args.pre,
            "post_path": args.post,
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
