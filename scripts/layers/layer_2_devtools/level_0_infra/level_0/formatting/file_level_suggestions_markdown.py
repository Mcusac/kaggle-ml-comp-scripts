"""Markdown formatting for file-level suggestions."""

from __future__ import annotations

from typing import Any, Iterable


def build_file_level_suggestions_markdown(payload: dict[str, Any]) -> str:
    generated = str(payload.get("generated", ""))
    scope = str(payload.get("scope", ""))
    root = str(payload.get("root", ""))
    counts = payload.get("counts", {}) or {}
    rows = payload.get("rows", []) or []

    lines: list[str] = [
        "---",
        f"generated: {generated}",
        "artifact: file_level_suggestions",
        "schema: file_level_suggestions.v1",
        f"scope: {scope}",
        f"root: {root}",
        "---",
        "",
        "# File level suggestions",
        "",
        "This report suggests minimal valid tiers (and flags conflicts) based on:",
        "- outgoing imports (lower bound)",
        "- incoming importers (upper bound constraint)",
        "",
        "## Summary",
        "",
    ]

    for k in sorted(counts.keys()):
        lines.append(f"- **{k}:** {counts.get(k)}")
    lines.append("")

    conflicts = [r for r in rows if (r.get("status") == "conflict")]
    moves = [
        r
        for r in rows
        if r.get("status") == "ok"
        and r.get("current_level") is not None
        and r.get("suggested_level") is not None
        and int(r.get("suggested_level")) != int(r.get("current_level"))
    ]
    no_change = [r for r in rows if r.get("status") == "no_change"]
    unknown = [r for r in rows if r.get("status") == "unknown"]

    lines.extend(_section("Conflicts", conflicts))
    lines.extend(_section("Moves suggested", moves))
    lines.extend(_section("No change", no_change))
    lines.extend(_section("Unknown / skipped", unknown))

    return "\n".join(lines).rstrip("\n") + "\n"


def _section(title: str, rows: Iterable[dict[str, Any]]) -> list[str]:
    rows = list(rows)
    lines: list[str] = [f"## {title}", ""]
    if not rows:
        lines.append("_None._")
        lines.append("")
        return lines

    for r in sorted(rows, key=lambda x: str(x.get("module", ""))):
        mod = str(r.get("module", ""))
        cur = r.get("current_level")
        lb = r.get("lb_required")
        ub = r.get("ub_allowed")
        sug = r.get("suggested_level")
        lines.append(f"### `{mod}`")
        lines.append("")
        lines.append(f"- **current_level:** {cur}")
        lines.append(f"- **lb_required:** {lb}")
        lines.append(f"- **ub_allowed:** {ub}")
        lines.append(f"- **suggested_level:** {sug}")

        out_dr = r.get("outgoing_drivers") or []
        in_dr = r.get("incoming_drivers") or []

        if out_dr:
            lines.append("- **outgoing_drivers:**")
            for e in out_dr:
                lines.append(
                    f"  - `{e.get('referenced', '')}` (level {e.get('referenced_level')})"
                )
        if in_dr:
            lines.append("- **incoming_drivers:**")
            for e in in_dr:
                lines.append(
                    f"  - importer `{e.get('module', '')}` (level {e.get('referenced_level')}) via `{e.get('referenced', '')}`"
                )
        lines.append("")
    return lines

