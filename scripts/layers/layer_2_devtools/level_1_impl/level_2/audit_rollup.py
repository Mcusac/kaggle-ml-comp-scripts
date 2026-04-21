#!/usr/bin/env python3
"""
Build a skeleton comprehensive rollup markdown from an audit queue JSON.

Optionally counts precheck JSON files per target for a given date. Does not
replace human-written theme summaries.

From ``kaggle-ml-comp-scripts/scripts/``::

  python -m layers.layer_2_devtools.level_1_impl.level_2.audit_rollup
"""

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_SCRIPTS_ROOT = _SCRIPT_DIR.parents[3]
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_1.api_audit import build_audit_rollup_from_queue_path


def main() -> int:
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding="utf-8", errors="replace"
        )

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--queue",
        type=Path,
        required=True,
        help="JSON file from audit_targets.py --write-manifest",
    )
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=None,
        help="Workspace with .cursor/audit-results (default: discover)",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="YYYY-MM-DD for precheck filename match (default: today)",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default="rollup-skeleton",
        help="Run id for frontmatter",
    )
    parser.add_argument(
        "--user-request",
        type=str,
        default="_(paste USER_REQUEST here)_",
        help="Verbatim user request or placeholder",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Write markdown to this path (default: print stdout)",
    )
    args = parser.parse_args()
    env = build_audit_rollup_from_queue_path(
        {
            "queue_path": args.queue,
            "scripts_root": _SCRIPTS_ROOT,
            "workspace_root": args.workspace_root,
            "generated": args.date,
            "run_id": args.run_id,
            "user_request": args.user_request,
            "output": args.output,
        }
    )
    if env["status"] != "ok":
        raise SystemExit("\n".join(env["errors"]))
    md = env["data"]["markdown"]
    if args.output:
        print(f"[OK] Wrote {args.output}", file=sys.stderr)
    else:
        print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
