"""
Import auto-fixer (rewrite-only).

Scans a target subtree (default: scripts/layers/) and applies conservative import rewrites:
- Deep general-stack imports rewritten to barrel imports only when provable via level_N/__init__.py exports
- Mixed layer_0_core import style rewritten to explicit `layers.layer_0_core.level_N` form
- Optional: rewrite relative imports in logic files to absolute imports when resolvable and non-deep
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

_SCRIPTS_ROOT = Path(__file__).resolve().parents[3]
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import err, ok
from layers.layer_2_devtools.level_0_infra.level_0.fix.import_fix_strategies import (
    FixOptions,
    build_edit_operations_for_tree,
)
from layers.layer_2_devtools.level_0_infra.level_0.fix.import_rewrite_engine import (
    apply_edit_operations,
)
from layers.layer_2_devtools.level_1_impl.level_1.api_maintenance import (
    run_verify_imports_cli_api,
)


def main() -> int:
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=_SCRIPTS_ROOT / "layers",
        help="Root directory to scan (default: scripts/layers).",
    )
    parser.add_argument("--apply", action="store_true", help="Apply edits (default: dry-run).")
    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Include files matching test_*.py (default: excluded).",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="After --apply, run verify_imports on layer_0_core to report remaining violations.",
    )
    parser.add_argument(
        "--max-changes-per-file",
        type=int,
        default=25,
        help="Safety cap on number of edits per file (default: 25).",
    )
    parser.add_argument(
        "--rewrite-relative-in-logic",
        type=str,
        default="off",
        choices=["off", "absolute"],
        help="If 'absolute', rewrite relative imports in logic files when resolvable and safe.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    if not root.is_dir():
        print(f"❌ root is not a directory: {root}", file=sys.stderr)
        return 2

    ops, build_errors = build_edit_operations_for_tree(
        root=root,
        scripts_root=_SCRIPTS_ROOT,
        opts=FixOptions(
            include_tests=bool(args.include_tests),
            rewrite_relative_in_logic=str(args.rewrite_relative_in_logic),
        ),
    )
    for e in build_errors:
        print(f"⚠️ {e}", file=sys.stderr)

    results, summary, apply_errors = apply_edit_operations(
        ops,
        apply=bool(args.apply),
        max_changes_per_file=max(0, int(args.max_changes_per_file)),
    )
    for e in apply_errors:
        print(f"⚠️ {e}", file=sys.stderr)

    changed = [r for r in results if r.edits_applied > 0]
    print(
        f"✅ files_considered={summary.files_considered} "
        f"files_changed={summary.files_changed} edits_applied={summary.edits_applied}"
    )
    if changed:
        print("files:")
        for r in changed:
            print(f"- {r.path.as_posix()} (edits={r.edits_applied})")

    if args.verify and args.apply:
        layer_0_core = _SCRIPTS_ROOT / "layers" / "layer_0_core"
        env = run_verify_imports_cli_api(
            {
                "scripts_root": _SCRIPTS_ROOT,
                "root": layer_0_core.resolve(),
                "include_tests": bool(args.include_tests),
                "write_json": False,
            }
        )
        if env["status"] != "ok":
            print("\n".join(env["errors"]), file=sys.stderr)
            return 1
        data = env["data"]
        print(f"✅ [VERIFY] Wrote {data['md_path']}")
        print(data["summary_line"])

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

