"""One-off Phase 2 scanner: emit tier violation data for RUN_PHASE2_MOVE_LIST.md."""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

ARC_PREFIX = "layers.layer_1_competition.level_1_impl.level_arc_agi_2"
ROOT = Path(__file__).resolve().parent
RE_LEVEL = re.compile(r"layers\.layer_1_competition\.level_1_impl\.level_arc_agi_2\.level_(\d+)")


def module_path_from_file(p: Path) -> str:
    rel = p.relative_to(ROOT).with_suffix("")
    return ".".join(rel.parts)


def file_tier(p: Path) -> int | None:
    rel = p.relative_to(ROOT)
    if not rel.parts:
        return None
    m = re.match(r"level_(\d+)", rel.parts[0])
    return int(m.group(1)) if m else None


def walk_import_modules(tree: ast.AST):
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            yield node.module
        elif isinstance(node, ast.Import):
            for alias in node.names:
                yield alias.name


def analyze_file(p: Path) -> tuple[int | None, set[int], list[str]]:
    tier = file_tier(p)
    if tier is None:
        return None, set(), []
    text = p.read_text(encoding="utf-8")
    try:
        tree = ast.parse(text)
    except SyntaxError as e:
        return tier, set(), [f"SYNTAX_ERROR: {e}"]
    imported_levels: set[int] = set()
    detail: list[str] = []
    mod_self = module_path_from_file(p)
    for mod in walk_import_modules(tree):
        if not mod or not mod.startswith(ARC_PREFIX):
            continue
        m = RE_LEVEL.search(mod)
        if not m:
            continue
        j = int(m.group(1))
        imported_levels.add(j)
        if mod == mod_self or mod.startswith(mod_self + "."):
            continue
        if j >= tier:
            detail.append(f"level_{j}: {mod}")
    return tier, imported_levels, detail


def propose_target_rel(rel: str, new_tier: int) -> str:
    parts = rel.split("/")
    parts[0] = f"level_{new_tier}"
    return "/".join(parts)


def main() -> int:
    rows: list[dict] = []
    for p in sorted(ROOT.rglob("*.py")):
        if p.name == "__init__.py" or p.name.startswith("_phase2_"):
            continue
        tier, levels, violations = analyze_file(p)
        if tier is None:
            continue
        max_j = max(levels) if levels else -1
        min_required = max_j + 1 if levels else 0
        rel = p.relative_to(ROOT).as_posix()
        needs_move = tier < min_required
        syntax_issues = [v for v in violations if v.startswith("SYNTAX_ERROR")]
        tier_violations = [v for v in violations if not v.startswith("SYNTAX_ERROR")]
        target_rel = propose_target_rel(rel, min_required) if needs_move else rel
        rows.append(
            {
                "path": rel,
                "tier": tier,
                "max_import_j": max_j,
                "min_required_tier": min_required,
                "needs_move": needs_move,
                "target_path": target_rel,
                "violations": tier_violations,
                "syntax_issues": syntax_issues,
            }
        )

    out = {
        "root": str(ROOT),
        "rule": "min_required_tier = max(imported arc level_J) + 1; move if current tier < min_required_tier",
        "files": rows,
    }
    json_path = ROOT / "_phase2_scan_output.json"
    json_path.write_text(json.dumps(out, indent=2), encoding="utf-8")

    violating = [r for r in rows if r["needs_move"]]
    parse_broken = [r for r in rows if r["syntax_issues"]]

    existing_levels: set[int] = set()
    for d in ROOT.iterdir():
        if d.is_dir() and d.name.startswith("level_"):
            try:
                existing_levels.add(int(d.name.split("_", 1)[1]))
            except ValueError:
                pass
    target_levels: set[int] = set()
    for r in violating:
        head = r["target_path"].split("/", 1)[0]
        try:
            target_levels.add(int(head.split("_", 1)[1]))
        except (ValueError, IndexError):
            pass
    new_package_levels = sorted(target_levels - existing_levels)

    # Target collision: multiple sources map to identical target_path
    target_to_sources: dict[str, list[str]] = {}
    for r in violating:
        target_to_sources.setdefault(r["target_path"], []).append(r["path"])
    collisions = {t: srcs for t, srcs in target_to_sources.items() if len(srcs) > 1}

    # Target exists on disk but is not the source (manual check)
    occupied: list[tuple[str, str]] = []
    for r in violating:
        tp = ROOT / r["target_path"]
        sp = ROOT / r["path"]
        if tp.exists() and tp.resolve() != sp.resolve():
            occupied.append((r["path"], r["target_path"]))

    lines: list[str] = [
        "# ARC Phase 2 — move list (tier scan)",
        "",
        "**Generated:** 2026-04-20. **Scanner:** `_phase2_scan_arc_tiers.py` (also writes `_phase2_scan_output.json`).",
        "",
        "## Rule",
        "",
        "For each non-`__init__.py` module under `level_arc_agi_2`, parse static imports of",
        "`layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_J.*`.",
        "",
        "- `max_J` = maximum `J` among those imports.",
        "- `min_required_tier` = `max_J + 1` if any arc import exists, else `0` (leaf modules).",
        "- **Violation** when file lives under `level_K` with `K < min_required_tier`.",
        "",
        "**Proposed path:** replace the first path segment `level_K` with `level_{min_required_tier}`, keep the rest.",
        "Phase 3 must confirm no semantic clash with existing packages and update all importers.",
        "",
        "## Summary",
        "",
        f"- Logic modules scanned: **{len(rows)}**",
        f"- Need tier lift (`git mv`): **{len(violating)}**",
        f"- AST parse issues (fix BOM/syntax before relying on scan): **{len(parse_broken)}**",
        f"- Duplicate proposed targets (resolve ordering / merge): **{len(collisions)}**",
        f"- Proposed target path already exists (review): **{len(occupied)}**",
        f"- Existing `level_N` dirs on disk (numeric): **{sorted(existing_levels)}**",
        f"- New `level_N` package roots required after moves: **{new_package_levels or 'none'}**",
        "",
    ]

    if new_package_levels:
        lines.extend(
            [
                "## New package tiers (Phase 3)",
                "",
                "Create these directories with `__init__.py` (and contest registration if required) before or with `git mv`:",
                "",
            ]
        )
        for n in new_package_levels:
            lines.append(f"- `level_{n}/` (currently missing under `level_arc_agi_2/`)")
        lines.append("")

    if parse_broken:
        lines.extend(
            [
                "## Parse issues (not tier-ranked)",
                "",
            ]
        )
        for r in sorted(parse_broken, key=lambda x: x["path"]):
            lines.append(f"- `{r['path']}`: {r['syntax_issues']}")
        lines.append("")

    if collisions:
        lines.extend(["## Proposed target collisions", ""])
        for t, srcs in sorted(collisions.items()):
            lines.append(f"- `{t}` ← " + ", ".join(f"`{s}`" for s in srcs))
        lines.append("")

    if occupied:
        lines.extend(["## Proposed target already on disk", ""])
        for src, tgt in sorted(occupied):
            lines.append(f"- `{src}` → `{tgt}` (destination exists)")
        lines.append("")

    lines.extend(
        [
            "## Moves (source → target)",
            "",
            "| Current | Target | min tier | Sample offending imports |",
            "|---------|--------|----------|---------------------------|",
        ]
    )
    for r in sorted(violating, key=lambda x: (x["min_required_tier"], x["path"])):
        samp = "; ".join(r["violations"][:2]) if r["violations"] else "(see max_J)"
        if len(r["violations"]) > 2:
            samp += "; …"
        lines.append(
            f"| `{r['path']}` | `{r['target_path']}` | {r['min_required_tier']} | {samp} |"
        )

    lines.extend(
        [
            "",
            "## `K >= 1` only (subset for staged Phase 3)",
            "",
            "| Current | Target | min tier |",
            "|---------|--------|----------|",
        ]
    )
    for r in sorted((x for x in violating if x["tier"] >= 1), key=lambda x: (x["min_required_tier"], x["path"])):
        lines.append(f"| `{r['path']}` | `{r['target_path']}` | {r['min_required_tier']} |")

    lines.extend(
        [
            "",
            "## `level_0` lifts (large batch — may follow `K>=1` passes)",
            "",
            "| Current | Target | min tier |",
            "|---------|--------|----------|",
        ]
    )
    for r in sorted((x for x in violating if x["tier"] == 0), key=lambda x: (x["min_required_tier"], x["path"])):
        lines.append(f"| `{r['path']}` | `{r['target_path']}` | {r['min_required_tier']} |")

    lines.extend(
        [
            "",
            "## SCC / cycle note",
            "",
            "This scan does not compute import cycles. Dense same-tier clusters (`level_2/lm`,",
            "`level_3/llm_tta_runner`, `level_0/notebook_commands`) may require **merge** or",
            "**lazy imports** after moves if circular dependencies appear at import time.",
            "",
        ]
    )

    md_path = ROOT / "RUN_PHASE2_MOVE_LIST.md"
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"OK wrote {json_path}")
    print(f"OK wrote {md_path}")
    print(f"Total logic files: {len(rows)}")
    print(f"Files needing tier lift: {len(violating)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
