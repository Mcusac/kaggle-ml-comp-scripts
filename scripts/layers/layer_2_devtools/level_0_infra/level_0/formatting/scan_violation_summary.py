"""Summarize level violation scan JSON for console output."""

from collections import defaultdict
from typing import Any


def format_scan_violation_summary_lines(data: dict[str, Any]) -> list[str]:
    """Build text lines describing violations by kind from scan payload."""
    by_kind: dict[str, list[str]] = defaultdict(list)
    for v in data.get("violations", []):
        by_kind[v["kind"]].append(v["file"])
    lines: list[str] = []
    lines.append(f"[SCAN] generated: {data.get('generated')}")
    lines.append("[SCAN] violations by kind:")
    for kind in (
        "DEEP_PATH",
        "RELATIVE_IN_LOGIC",
        "WRONG_LEVEL",
        "UPWARD",
        "PARSE_ERROR",
    ):
        files = sorted(set(by_kind.get(kind, [])))
        if files:
            lines.append(f"  {kind}: {len(files)} file(s)")
            for f in files:
                lines.append(f"    - {f}")
    pe = data.get("parse_errors") or []
    if pe:
        lines.append(f"  PARSE_ERROR entries: {len(pe)}")
    return lines