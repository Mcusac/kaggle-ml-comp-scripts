"""
Import organizer (top-of-file reordering only).

Applies deterministic grouping and spacing rules from `python-import-order.mdc`.
This tool is rewrite-only: it does not remove unused imports or change import surfaces.
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

_SCRIPTS_ROOT = Path(__file__).resolve().parents[3]
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import err
from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import ok
from layers.layer_2_devtools.level_1_impl.level_1.api_maintenance import (
    run_import_organizer_cli_api,
)


def _win_utf8_stdio() -> None:
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def main() -> int:
    _win_utf8_stdio()
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
        "--max-files",
        type=int,
        default=None,
        help="Optional max number of files to process.",
    )
    args = parser.parse_args()

    env = run_import_organizer_cli_api(
        {
            "root": args.root,
            "apply": bool(args.apply),
            "include_tests": bool(args.include_tests),
            "max_files": args.max_files,
        }
    )
    if env["status"] != "ok":
        print("\n".join(env["errors"]), file=sys.stderr)
        return 1

    data = env["data"]
    warnings = list(data.get("warnings") or [])
    for w in warnings:
        print(f"⚠️ {w}", file=sys.stderr)

    print(
        "✅ "
        f"files_considered={data.get('files_considered')} "
        f"files_changed={data.get('files_changed')} "
        f"edits_applied={data.get('edits_applied')}"
    )
    changed = data.get("changed_files") or []
    if changed:
        print("files:")
        for p in changed:
            print(f"- {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

