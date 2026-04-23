"""
Import verification script.

Verifies all imports in the codebase are valid and can be resolved.
"""

import argparse
import io
import sys
from datetime import date
from pathlib import Path

_SCRIPTS_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_1.api_maintenance import (
    run_verify_imports_cli_api,
)


def main() -> int:
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    default_root = _SCRIPTS_ROOT / "layers" / "layer_0_core"

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=default_root,
        help="Root directory to scan (default: scripts/layers/layer_0_core).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Write reports here (default: <workspace>/.cursor/audit-results/general/audits).",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="YYYY-MM-DD for filenames (default: today).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Also write verify_imports_scan_<date>.json next to the .md report.",
    )
    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Include files matching test_*.py (default: excluded).",
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
        help="Exit 1 if any file failed to parse in surface scan.",
    )
    args = parser.parse_args()

    generated = date.fromisoformat(args.date) if args.date else date.today()
    env = run_verify_imports_cli_api(
        {
            "scripts_root": _SCRIPTS_ROOT,
            "root": args.root.resolve(),
            "output_dir": args.output_dir.resolve() if args.output_dir else None,
            "generated": generated,
            "include_tests": bool(args.include_tests),
            "write_json": bool(args.json),
        }
    )
    if env["status"] != "ok":
        print("\n".join(env["errors"]), file=sys.stderr)
        return 1
    data = env["data"]
    print(f"✅ [OK] Wrote {data['md_path']}")
    if "json_path" in data:
        print(f"✅ [OK] Wrote {data['json_path']}")
    print(data["summary_line"])

    exit_code = 0
    if args.fail_on_violations:
        max_v = max(0, int(args.max_violations))
        vcount = int(data.get("violation_count", 0))
        if vcount > max_v:
            print(
                f"❌ [FAIL] violation_count={vcount} exceeds --max-violations={max_v}",
                file=sys.stderr,
            )
            exit_code = 1
    if args.fail_on_parse_errors and int(data.get("parse_error_count", 0)) > 0:
        print(
            f"❌ [FAIL] parse_error_count={data.get('parse_error_count')}",
            file=sys.stderr,
        )
        exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
