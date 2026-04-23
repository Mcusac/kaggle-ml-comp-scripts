"""Draft move checklists from ``level_violations_scan_*.json`` (no file moves, human-in-the-loop v1)."""

from __future__ import annotations

from typing import Any


def build_move_plan_markdown(data: dict[str, Any]) -> str:
    """
    Build a short markdown checklist: one section per file with a ``suggested_min_level``.

    Does not generate patches or move files.
    """
    lines: list[str] = [
        "---",
        f"generated: {data.get('generated', '')}",
        "kind: level_violations_move_plan_draft",
        f"source_artifact: {data.get('artifact', '')}",
        "---",
        "",
        "# Level violation move plan (draft)",
        "",
        "Heuristic `suggested_min_level` comes from the scan: a logic file using "
        "``from level_I import`` should live under at least "
        "``.../level_(I+1)/...`` (see `python-import-surfaces.mdc`).",
        "",
        "Steps for each file (manual or scripted later):",
        "",
        "1. Create the target `level_M` path if needed.",
        "2. Move the file; fix any relative imports and callers.",
        "3. Run `regenerate_package_inits` on the affected tree.",
        "",
    ]
    seen: set[str] = set()
    for v in data.get("violations", []):
        sug = v.get("suggested_min_level")
        if sug is None:
            continue
        f = v.get("file", "")
        key = f"{f}|{sug}"
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"## `{f}`")
        lines.append("")
        lines.append(f"- **kind:** `{v.get('kind')}` (line {v.get('line')})")
        lines.append(
            f"- **file_level:** {v.get('file_level', 'n/a')}"
            f"  |  **suggested_min_level:** {sug}"
        )
        lines.append(
            f"- **Approximate target:** under `level_{sug}/` in the same package (adjust for your layout)."
        )
        lines.append(f"- {v.get('detail', '')}")
        lines.append("")
    if len(seen) == 0:
        lines.append("_No entries with `suggested_min_level` in this scan._")
        lines.append("")
    return "\n".join(lines)
