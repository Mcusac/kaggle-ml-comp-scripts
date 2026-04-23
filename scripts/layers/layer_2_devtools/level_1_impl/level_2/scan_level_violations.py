"""
Scan general stack level_0 .. level_10 for import layering violations.

Read-only: writes a markdown report under .cursor/audit-results/general/audits/.
"""

import argparse
import sys
from datetime import date
from pathlib import Path

_SCRIPTS_ROOT = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_0_infra.level_0.formatting.move_plan_from_scan import (
    build_move_plan_markdown,
)
from layers.layer_2_devtools.level_1_impl.level_1.api_audit import run_general_stack_scan_with_artifacts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    default_scripts = (
        Path(__file__).resolve().parent.parent / "layers" / "layer_0_core"
    )
    parser.add_argument(
        "--scripts-dir",
        type=Path,
        default=default_scripts,
        help=(
            "Directory containing level_0 .. level_10 "
            "(default: scripts/layers/layer_0_core)"
        ),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Markdown report path (default: .cursor/audit-results/general/audits/)",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="YYYY-MM-DD for filename (default: today)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Also write level_violations_scan_<date>.json next to the .md report",
    )
    parser.add_argument(
        "--emit-move-plan",
        action="store_true",
        help=(
            "Write level_violations_move_plan_<date>.md (draft checklist; uses scan payload). "
            "Does not require --json."
        ),
    )
    parser.add_argument(
        "--fail-on-violations",
        action="store_true",
        help="Exit with code 1 if violation_count exceeds --max-violations (default 0).",
    )
    parser.add_argument(
        "--max-violations",
        type=int,
        default=0,
        help="When using --fail-on-violations, allow up to this many violations (default: 0).",
    )
    parser.add_argument(
        "--fail-on-parse-errors",
        action="store_true",
        help="Exit with code 1 if any file had a parse error (in addition to violation checks).",
    )
    args = parser.parse_args()
    scripts_dir = args.scripts_dir.resolve()

    generated = date.fromisoformat(args.date) if args.date else date.today()
    env = run_general_stack_scan_with_artifacts(
        {
            "scripts_dir": scripts_dir,
            "generated": generated,
            "output": args.output,
            "write_json": bool(args.json),
        }
    )
    if env["status"] != "ok":
        raise SystemExit("\n".join(env["errors"]))
    data = env["data"]
    print(f"[OK] Wrote {data['md_path']}")
    if "json_path" in data:
        print(f"[OK] Wrote {data['json_path']}")
    if args.emit_move_plan:
        md_path = Path(data["md_path"])
        plan_path = md_path.parent / (
            f"level_violations_move_plan_{generated.isoformat()}.md"
        )
        plan_path.write_text(
            build_move_plan_markdown(data["payload"]),
            encoding="utf-8",
        )
        print(f"[OK] Wrote {plan_path}")
    print(data["summary_line"])

    exit_code = 0
    if args.fail_on_violations:
        max_v = max(0, int(args.max_violations))
        vcount = int(data.get("violation_count", 0))
        if vcount > max_v:
            print(
                f"[FAIL] violation_count={vcount} exceeds --max-violations={max_v}",
                file=sys.stderr,
            )
            exit_code = 1
    if args.fail_on_parse_errors and int(data.get("parse_error_count", 0)) > 0:
        print(
            f"[FAIL] parse_error_count={data.get('parse_error_count')}",
            file=sys.stderr,
        )
        exit_code = 1
    if exit_code:
        raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
