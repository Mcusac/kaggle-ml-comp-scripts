"""Run code-fix machine pipeline (deterministic; emits FIX_RUN summary).

This CLI orchestrates existing fix tools via `run_code_fix_pipeline` and writes a
single FIX_RUN markdown artifact under `.cursor/audit-results/<scope>/summaries/`.

Run from: `input/kaggle-ml-comp-scripts/scripts/`

Example:
  python -m layers.layer_2_devtools.level_1_impl.level_2.run_code_fix_pipeline --target-root layers/layer_0_core/level_2 --dry-run
  python -m layers.layer_2_devtools.level_1_impl.level_2.run_code_fix_pipeline --target-root layers/layer_0_core/level_2 --apply --tools fix_imports organize_imports init_regen verify_imports
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

from layers.layer_2_devtools.level_1_impl.level_1.api_fix_pipeline import run_code_fix_pipeline


def _win_utf8_stdio() -> None:
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def main() -> int:
    _win_utf8_stdio()

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--scripts-root",
        type=Path,
        default=Path(__file__).resolve().parents[3],
        help="scripts/ root (default: inferred from this file).",
    )
    p.add_argument(
        "--target-root",
        type=Path,
        required=True,
        help="Target tree under scripts/ (e.g. layers/layer_0_core/level_2).",
    )
    p.add_argument(
        "--audit-scope",
        type=str,
        default=None,
        choices=["general", "competition_infra", "contests_special"],
        help="Override audit scope (default: derived from path).",
    )
    p.add_argument(
        "--level-name",
        type=str,
        default=None,
        help="Override level name/slug used in FIX_RUN filename.",
    )
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="Apply edits (default: dry-run).")
    mode.add_argument("--dry-run", action="store_true", help="Dry-run (default).")
    p.add_argument("--include-tests", action="store_true", help="Include test_*.py where supported.")
    p.add_argument(
        "--tools",
        nargs="*",
        default=[],
        help="Tools to run (in order). Default runs the full common set.",
    )
    p.add_argument(
        "--scan-json",
        type=Path,
        default=None,
        help="Optional scan JSON path for apply_violation_fixes.",
    )
    p.add_argument(
        "--audits-dir",
        type=Path,
        default=None,
        help="Optional audits dir containing level_violations_scan_*.json for apply_violation_fixes.",
    )
    p.add_argument(
        "--unused-imports-report",
        type=Path,
        default=None,
        help="Optional health report JSON for cleanup_imports.",
    )
    p.add_argument(
        "--cleanup-no-organize-imports",
        action="store_true",
        help="Skip deterministic import organization after unused-import cleanup.",
    )
    p.add_argument(
        "--cleanup-format",
        action="store_true",
        help="Run external formatter after cleanup_imports edits (off by default).",
    )
    p.add_argument(
        "--cleanup-format-tool",
        choices=["ruff", "black"],
        default="ruff",
        help="Formatter to use when --cleanup-format is enabled.",
    )
    p.add_argument(
        "--cleanup-format-args",
        action="append",
        default=[],
        help="Extra formatter args (repeatable).",
    )
    args = p.parse_args()

    scripts_root = args.scripts_root.resolve()
    target_root = (scripts_root / args.target_root).resolve() if not args.target_root.is_absolute() else args.target_root.resolve()
    if not target_root.is_dir():
        print(f"❌ target_root is not a directory: {target_root}", file=sys.stderr)
        return 2

    env = run_code_fix_pipeline(
        {
            "scripts_root": scripts_root,
            "target_root": target_root,
            "audit_scope": args.audit_scope,
            "level_name": args.level_name,
            "apply": bool(args.apply),
            "include_tests": bool(args.include_tests),
            "tools": list(args.tools or []),
            "scan_json": str(args.scan_json) if args.scan_json else None,
            "audits_dir": str(args.audits_dir) if args.audits_dir else None,
            "unused_imports_report": str(args.unused_imports_report) if args.unused_imports_report else None,
            "cleanup_no_organize_imports": bool(args.cleanup_no_organize_imports),
            "cleanup_format": bool(args.cleanup_format),
            "cleanup_format_tool": args.cleanup_format_tool,
            "cleanup_format_args": list(args.cleanup_format_args or []),
        }
    )
    if env["status"] != "ok":
        print("\n".join(env.get("errors") or ["unknown error"]), file=sys.stderr)
        return 1

    data = env["data"]
    print(f"✅ FIX_RUN written: {data['fix_run_path']}")
    if data.get("errors"):
        print(f"❌ errors={len(data['errors'])}", file=sys.stderr)
        return 1
    return int(data.get("overall_exit_code", 0) or 0)


if __name__ == "__main__":
    raise SystemExit(main())

