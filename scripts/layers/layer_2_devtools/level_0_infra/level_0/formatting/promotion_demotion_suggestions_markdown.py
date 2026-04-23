"""Markdown formatting for promotion/demotion suggestions."""

from __future__ import annotations

from typing import Any, Iterable


def build_promotion_demotion_suggestions_markdown(payload: dict[str, Any]) -> str:
    generated = str(payload.get("generated", ""))
    scope = str(payload.get("scope", ""))
    root = str(payload.get("root", ""))
    counts = payload.get("counts", {}) or {}
    promo_rows = payload.get("promotion_rows", []) or []
    demo_rows = payload.get("demotion_rows", []) or []

    lines: list[str] = [
        "---",
        f"generated: {generated}",
        "artifact: promotion_demotion_suggestions",
        "schema: promotion_demotion_suggestions.v1",
        f"scope: {scope}",
        f"root: {root}",
        "---",
        "",
        "# Promotion / demotion suggestions",
        "",
        "This report analyzes inbound usage (who imports a module) and summarizes:",
        "- cross-level usage counts",
        "- heavy-reuse promotion candidates",
        "- demotion candidates used only by lower levels",
        "",
        "## Summary",
        "",
    ]

    lines.extend(_lines_counts(counts))
    lines.append("")

    promo_ok = [r for r in promo_rows if r.get("status") == "ok"]
    demo_ok = [r for r in demo_rows if r.get("status") == "ok"]

    lines.extend(_section_promotion("Promotion candidates", promo_ok))
    lines.extend(_section_demotion("Demotion candidates", demo_ok))

    return "\n".join(lines).rstrip("\n") + "\n"


def _lines_counts(counts: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    promo = counts.get("promotion", {}) or {}
    demo = counts.get("demotion", {}) or {}
    if promo:
        lines.append("- **promotion_status_counts:**")
        for k in sorted(promo.keys()):
            lines.append(f"  - **{k}:** {promo.get(k)}")
    else:
        lines.append("- **promotion_status_counts:** _none_")

    if demo:
        lines.append("- **demotion_status_counts:**")
        for k in sorted(demo.keys()):
            lines.append(f"  - **{k}:** {demo.get(k)}")
    else:
        lines.append("- **demotion_status_counts:** _none_")
    return lines


def _section_promotion(title: str, rows: Iterable[dict[str, Any]]) -> list[str]:
    rows = list(rows)
    lines: list[str] = [f"## {title}", ""]
    if not rows:
        lines.append("_None._")
        lines.append("")
        return lines

    for r in sorted(rows, key=lambda x: str(x.get("module", ""))):
        lines.extend(_lines_row(r, kind="promotion"))
    return lines


def _section_demotion(title: str, rows: Iterable[dict[str, Any]]) -> list[str]:
    rows = list(rows)
    lines: list[str] = [f"## {title}", ""]
    if not rows:
        lines.append("_None._")
        lines.append("")
        return lines

    for r in sorted(rows, key=lambda x: str(x.get("module", ""))):
        lines.extend(_lines_row(r, kind="demotion"))
    return lines


def _lines_row(r: dict[str, Any], *, kind: str) -> list[str]:
    mod = str(r.get("module", ""))
    cur = r.get("current_level")
    sug = r.get("suggested_level")
    inbound_total = r.get("inbound_total")
    levels = r.get("distinct_importer_levels") or []
    by_level = r.get("inbound_by_level") or {}
    heavy = r.get("heavy_reuse")

    lines: list[str] = [f"### `{mod}`", ""]
    lines.append(f"- **current_level:** {cur}")
    lines.append(f"- **suggested_level:** {sug}")
    lines.append(f"- **inbound_total:** {inbound_total}")
    lines.append(f"- **distinct_importer_levels:** {levels}")
    if kind == "promotion":
        lines.append(f"- **heavy_reuse:** {heavy}")
    if by_level:
        lines.append("- **inbound_by_level:**")
        for k in sorted(by_level.keys(), key=lambda x: int(x) if str(x).isdigit() else str(x)):
            lines.append(f"  - level_{k}: {by_level.get(k)}")

    top = r.get("top_importers") or []
    if top:
        lines.append("- **top_importers:**")
        for e in top[:10]:
            lines.append(
                f"  - importer `{e.get('importer_module', '')}` (level_{e.get('importer_level')})"
            )
    lines.append("")
    return lines

