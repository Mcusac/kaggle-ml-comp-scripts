"""Markdown skeleton for comprehensive audit rollup from queue JSON."""

from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_0_infra.level_0 import precheck_summary_json_path


def build_comprehensive_rollup_skeleton_markdown(
    queue: dict[str, Any],
    workspace: Path,
    generated: date,
    *,
    run_id: str,
    user_request_placeholder: str,
) -> str:
    """Build skeleton rollup markdown with precheck JSON presence table."""
    targets = queue.get("targets") or []
    by_scope: dict[str, int] = defaultdict(int)
    precheck_ok = 0
    precheck_missing = 0
    lines = [
        "---",
        f"generated: {generated.isoformat()}",
        f"run_id: {run_id}",
        "artifact: rollup_skeleton",
        "---",
        "",
        "# Comprehensive code-audit rollup (skeleton)",
        "",
        "## USER_REQUEST",
        "",
        user_request_placeholder,
        "",
        "## Resolved configuration (from queue file)",
        "",
        "| Field | Value |",
        "|--------|--------|",
        f"| preset | `{queue.get('preset', '')}` |",
        f"| layers_root | `{queue.get('layers_root', '')}` |",
        f"| target_count | {queue.get('target_count', len(targets))} |",
        "",
        "## Targets by audit_scope",
        "",
    ]
    for t in targets:
        by_scope[str(t.get("audit_scope", ""))] += 1
    for scope in sorted(by_scope.keys()):
        lines.append(f"- **{scope}:** {by_scope[scope]}")
    lines.extend(["", "## Precheck JSON presence (machine)", ""])
    for t in targets:
        scope = str(t.get("audit_scope", ""))
        name = str(t.get("level_name", ""))
        p = precheck_summary_json_path(workspace, scope, name, generated)
        if p.is_file():
            precheck_ok += 1
            status = f"yes — `{p.relative_to(workspace).as_posix()}`"
        else:
            precheck_missing += 1
            status = "_missing_"
        lines.append(f"- `{name}` ({scope}): {status}")
    lines.extend(
        [
            "",
            f"**Summary:** {precheck_ok} precheck JSON file(s) found for date "
            f"{generated.isoformat()}, {precheck_missing} missing.",
            "",
            "## Primary artifact paths",
            "",
            "Inventories: `.cursor/audit-results/<scope>/inventories/INVENTORY_<level>.md`",
            "",
            "Audits: `.cursor/audit-results/<scope>/audits/<level>_audit.md`",
            "",
            "## Highest-severity themes",
            "",
            "_Fill in after planner/auditor runs._",
            "",
        ]
    )
    return "\n".join(lines)