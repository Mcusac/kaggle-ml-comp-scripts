#!/usr/bin/env python3
"""
DEPRECATED — not a substitute for code-audit-planner / code-audit-auditor.

This script templates INVENTORY_*.md and *_audit.md from precheck + bootstrap.
Per `.cursor/agents/code-audit-orchestrator-details.md` Step 0.8, normal audits must invoke the
planner and auditor subagents; use this ONLY when USER_REQUEST explicitly opts
into machine emit (e.g. "machine emit only", "use emit script") or for local
CI/skeleton experiments. May be removed in a future cleanup.

Legacy: Step 2.7 (precheck) + emit for each row in an audit_targets manifest.

Run from scripts/:  python dev/scripts/comprehensive_audit_emit.py --manifest <queue.json>
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_SCRIPTS_ROOT = _SCRIPT_DIR.parent.parent
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_1.api_audit_emit import (
    run_comprehensive_audit_emit_cli_api,
)


def main() -> int:
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding="utf-8", errors="replace"
        )

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--workspace", type=Path, default=None)
    p.add_argument("--generated", type=str, default=None, help="YYYY-MM-DD")
    p.add_argument("--run-id", type=str, default="comprehensive-emit")
    p.add_argument("--pass-number", type=int, default=1)
    p.add_argument(
        "--skip-precheck",
        action="store_true",
        help="Only emit inventory/audit (precheck .md/.json must already exist)",
    )
    args = p.parse_args()
    env = run_comprehensive_audit_emit_cli_api(
        {
            "manifest": args.manifest,
            "workspace_root": args.workspace,
            "generated": args.generated,
            "run_id": args.run_id,
            "pass_number": args.pass_number,
            "skip_precheck": args.skip_precheck,
            "scripts_root": _SCRIPTS_ROOT,
        }
    )
    if env["status"] != "ok":
        raise SystemExit("\n".join(env["errors"]))
    return int(env["data"]["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
