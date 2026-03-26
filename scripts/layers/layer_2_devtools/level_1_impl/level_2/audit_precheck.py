#!/usr/bin/env python3
"""
Run static import/layering precheck for one audit target; write markdown + JSON
under .cursor/audit-results/<scope>/summaries/.

Run from scripts/:  python dev/scripts/audit_precheck.py ...

Does not replace the planner/auditor; feeds machine findings for Phase 7 reconciliation.
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_SCRIPTS_ROOT = _SCRIPT_DIR.parent.parent
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_1.api_audit import run_audit_precheck_cli_complete


def _win_utf8_stdio() -> None:
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding="utf-8", errors="replace"
        )


def main() -> int:
    _win_utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--audit-scope",
        choices=("general", "competition_infra", "contests_special"),
        required=True,
    )
    parser.add_argument(
        "--level-path",
        type=Path,
        help="Directory (or file) under the audited level package",
    )
    parser.add_argument(
        "--level-name",
        type=str,
        required=True,
        help="Artifact key, e.g. level_3, level_csiro_level_1",
    )
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=None,
        help="Repo root with .cursor/audit-results (default: discover from level-path)",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="YYYY-MM-DD for filename (default: today)",
    )
    parser.add_argument(
        "--full-general-scan",
        action="store_true",
        help="general scope only: scan all layer_0..10 under default layer_0_core",
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Write only JSON (no markdown)",
    )
    parser.add_argument(
        "--precheck-kind",
        choices=("auto", "contest_tier", "contest_root", "special_tree"),
        default="auto",
        help=(
            "contests_special only: auto infers from path/name, or force tier / "
            "contest package root / layer_Z-style tree"
        ),
    )
    args = parser.parse_args()
    env = run_audit_precheck_cli_complete(
        {
            "scripts_root": _SCRIPTS_ROOT,
            "audit_scope": args.audit_scope,
            "level_name": args.level_name,
            "level_path": args.level_path,
            "workspace_root": args.workspace_root,
            "generated": args.date,
            "json_only": args.json_only,
            "full_general_scan": args.full_general_scan,
            "precheck_kind": args.precheck_kind,
        }
    )
    if env["status"] != "ok":
        raise SystemExit("\n".join(env["errors"]))
    for msg in env["data"]["messages"]:
        print(msg)
    return int(env["data"]["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
