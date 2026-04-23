"""Pure text builders for health JSON report summaries (CLI-agnostic)."""

from collections import defaultdict
from pathlib import Path
from typing import Any


def remap_duplicate_loc(loc: dict[str, Any]) -> str:
    module = loc.get("module") or loc.get("file") or "unknown"
    line = loc.get("line") or loc.get("start_line") or 0
    return f"{module}:{line}"


def extract_duplicate_blocks(duplication: dict[str, Any]) -> list[dict[str, Any]]:
    blocks = duplication.get("duplicate_blocks")
    if isinstance(blocks, list):
        return blocks
    blocks = duplication.get("duplicates")
    if isinstance(blocks, list):
        return blocks
    return []


def lines_duplication_summary(
    data: dict[str, Any],
    *,
    report_path: Path,
    top: int,
) -> list[str]:
    duplication = data.get("duplication", {}) if isinstance(data, dict) else {}
    blocks = extract_duplicate_blocks(duplication)
    total_lines = duplication.get("total_duplicate_lines") or duplication.get("duplicate_lines") or 0

    lines: list[str] = [
        "=" * 80,
        "DUPLICATION SUMMARY",
        "=" * 80,
        f"Report: {report_path}",
        f"Duplicate blocks: {len(blocks)}",
        f"Total duplicate lines: {total_lines}",
        "",
    ]

    if not blocks:
        return lines

    size_groups: dict[int, int] = {}
    for b in blocks:
        size = int(b.get("lines") or b.get("size") or 0)
        size_groups[size] = size_groups.get(size, 0) + 1

    lines.append("Top block sizes:")
    for size in sorted(size_groups.keys(), reverse=True)[:10]:
        lines.append(f"  {size:4} lines: {size_groups[size]}")
    lines.append("")

    def key_fn(x: dict[str, Any]) -> int:
        return int(x.get("lines") or x.get("size") or 0)

    lines.append(f"Top {top} largest blocks:")
    for i, b in enumerate(sorted(blocks, key=key_fn, reverse=True)[:top], 1):
        size = int(b.get("lines") or b.get("size") or 0)
        frequency = b.get("frequency") or 2

        if "file1" in b and "file2" in b:
            file1 = b.get("file1", "unknown")
            file2 = b.get("file2", "unknown")
            line1 = b.get("line1", 0)
            line2 = b.get("line2", 0)
            lines.append(f"{i:2}. {size} lines (frequency: {frequency})")
            lines.append(f"    - {file1}:{line1}")
            lines.append(f"    - {file2}:{line2}")
            continue

        locs = b.get("locations") if isinstance(b.get("locations"), list) else []
        lines.append(
            f"{i:2}. {size} lines (frequency: {frequency}) appears in {len(locs) or 'unknown'} locations"
        )
        for loc in locs[:3]:
            if isinstance(loc, dict):
                lines.append(f"    - {remap_duplicate_loc(loc)}")
        if len(locs) > 3:
            lines.append(f"    ... and {len(locs) - 3} more")

    return lines


def _count(items: object) -> int:
    return len(items) if isinstance(items, list) else 0


def _safe_int(x: object, default: int = 0) -> int:
    try:
        return int(x)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


def lines_oversized_modules(
    data: dict[str, Any],
    *,
    report_path: Path,
    max_file_lines: int,
    top: int,
    include_suggestions: bool,
) -> list[str]:
    file_metrics = data.get("file_metrics", {}) if isinstance(data, dict) else {}
    long_files = file_metrics.get("long_files", [])
    long_functions = file_metrics.get("long_functions", [])
    large_classes = file_metrics.get("large_classes", [])

    if not isinstance(long_files, list):
        long_files = []
    if not isinstance(long_functions, list):
        long_functions = []
    if not isinstance(large_classes, list):
        large_classes = []

    oversized = [
        f
        for f in long_files
        if isinstance(f, dict) and _safe_int(f.get("lines")) > max(0, int(max_file_lines))
    ]

    lines: list[str] = [
        "=" * 80,
        "OVERSIZED MODULES",
        "=" * 80,
        f"Report: {report_path}",
        f"Threshold: max_file_lines={max_file_lines}",
        f"Oversized modules: {len(oversized)}",
        "",
    ]

    if not oversized:
        lines.append("✅ No oversized modules detected.")
        lines.append("")
        return lines

    def key_fn(x: dict[str, Any]) -> int:
        return _safe_int(x.get("lines"))

    show = sorted(oversized, key=key_fn, reverse=True)[: max(0, int(top))]
    for i, row in enumerate(show, 1):
        module = str(row.get("module") or "unknown")
        loc = _safe_int(row.get("lines"))
        over_by = max(0, loc - int(max_file_lines))
        lines.append(f"{i:2}. {loc} lines (+{over_by})  {module}")

        if not include_suggestions:
            continue

        # Conservative heuristics driven only by existing file_metrics.
        hot_funcs = [
            f
            for f in long_functions
            if isinstance(f, dict)
            and str(f.get("module") or "") == module
            and _safe_int(f.get("lines")) >= 80
        ]
        hot_funcs.sort(key=lambda x: _safe_int(x.get("lines")), reverse=True)

        hot_classes = [
            c
            for c in large_classes
            if isinstance(c, dict)
            and str(c.get("module") or "") == module
            and _safe_int(c.get("methods")) >= 10
        ]
        hot_classes.sort(key=lambda x: _safe_int(x.get("methods")), reverse=True)

        suggestions: list[str] = []
        if hot_funcs:
            fn = str(hot_funcs[0].get("function") or "<?>")
            fl = _safe_int(hot_funcs[0].get("lines"))
            suggestions.append(f"Extract long function `{fn}` (~{fl} lines) into a submodule.")
        if len(hot_funcs) >= 2:
            fn2 = str(hot_funcs[1].get("function") or "<?>")
            fl2 = _safe_int(hot_funcs[1].get("lines"))
            suggestions.append(f"Split helper logic out of `{fn2}` (~{fl2} lines).")
        if hot_classes:
            cn = str(hot_classes[0].get("class") or "<?>")
            m = _safe_int(hot_classes[0].get("methods"))
            suggestions.append(f"Consider splitting class `{cn}` ({m} methods) into focused collaborators.")

        if not suggestions:
            suggestions.append(
                "No obvious hotspots from file-metrics; split by responsibility into submodules."
            )

        for s in suggestions[:3]:
            lines.append(f"    - Suggestion: {s}")

    if len(oversized) > len(show):
        lines.append("")
        lines.append(f"... and {len(oversized) - len(show)} more")
    lines.append("")
    return lines


def lines_health_compare(pre: dict[str, Any], post: dict[str, Any], *, pre_path: Path, post_path: Path) -> list[str]:
    pre_dead = pre.get("dead_code", {})
    post_dead = post.get("dead_code", {})
    pre_unused = int(pre_dead.get("total_unused_imports", 0) or 0)
    post_unused = int(post_dead.get("total_unused_imports", 0) or 0)

    pre_type = pre.get("type_annotations", {})
    post_type = post.get("type_annotations", {})
    pre_type_errors = _count(pre_type.get("missing_imports"))
    post_type_errors = _count(post_type.get("missing_imports"))

    pre_comp = pre.get("complexity", {})
    post_comp = post.get("complexity", {})
    pre_high_funcs = _count([f for f in pre_comp.get("functions", []) if (f.get("complexity", 0) or 0) >= 20])
    post_high_funcs = _count([f for f in post_comp.get("functions", []) if (f.get("complexity", 0) or 0) >= 20])
    pre_high_classes = _count([c for c in pre_comp.get("classes", []) if (c.get("complexity", 0) or 0) >= 50])
    post_high_classes = _count([c for c in post_comp.get("classes", []) if (c.get("complexity", 0) or 0) >= 50])

    lines = [
        "=" * 80,
        "HEALTH REPORT COMPARISON",
        "=" * 80,
        f"Pre:  {pre_path}",
        f"Post: {post_path}",
        "",
        "Unused imports:",
        f"  Before: {pre_unused}",
        f"  After:  {post_unused}",
    ]
    if pre_unused:
        lines.append(f"  Change: {post_unused - pre_unused} ({(post_unused - pre_unused) / pre_unused * 100:.1f}%)")
    else:
        lines.append("  Change: N/A")
    lines.extend(
        [
            "",
            "Type annotation missing imports:",
            f"  Before: {pre_type_errors}",
            f"  After:  {post_type_errors}",
            f"  Change: {post_type_errors - pre_type_errors}",
            "",
            "High complexity counts:",
            f"  Functions (>=20): before {pre_high_funcs}, after {post_high_funcs} (Δ {post_high_funcs - pre_high_funcs})",
            f"  Classes   (>=50): before {pre_high_classes}, after {post_high_classes} (Δ {post_high_classes - pre_high_classes})",
        ]
    )
    return lines


def lines_srp_summary(data: dict[str, Any], *, report_path: Path, top_modules: int) -> list[str]:
    solid = data.get("solid", {}) if isinstance(data, dict) else {}
    srp = solid.get("srp_violations", [])
    if not isinstance(srp, list):
        srp = []

    lines = [
        "=" * 80,
        "SRP VIOLATIONS SUMMARY",
        "=" * 80,
        f"Report: {report_path}",
        f"Total SRP violations: {len(srp)}",
        "",
    ]

    if not srp:
        return lines

    by_reason: dict[str, list[dict[str, Any]]] = defaultdict(list)
    by_module: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for v in srp:
        if not isinstance(v, dict):
            continue
        by_reason[str(v.get("reason", "unknown"))].append(v)
        by_module[str(v.get("module", "unknown"))].append(v)

    lines.append("Violations by reason:")
    for reason, items in sorted(by_reason.items(), key=lambda x: len(x[1]), reverse=True)[:15]:
        lines.append(f"  {reason}: {len(items)}")
    lines.append("")

    lines.append(f"Top {top_modules} modules with most violations:")
    for module, items in sorted(by_module.items(), key=lambda x: len(x[1]), reverse=True)[:top_modules]:
        lines.append(f"  {module}: {len(items)}")

    return lines


DEFAULT_COMPLEXITY_TARGET_NAMES = [
    "CAFAPostProcessor",
    "DeadCodeFinder",
    "BaseModelTrainer",
    "PerOntologyTrainWorkflow",
    "ConsoleReporter",
    "ProgressTracker",
    "FeatureExtractionTrainer",
]


def lines_complexity_targets(
    data: dict[str, Any],
    *,
    report_path: Path,
    targets: list[str],
) -> list[str]:
    complexity = data.get("complexity", {}) if isinstance(data, dict) else {}
    classes = complexity.get("classes", [])
    if not isinstance(classes, list):
        classes = []

    found: dict[str, dict] = {}
    for cls in classes:
        if not isinstance(cls, dict):
            continue
        name = str(cls.get("name", ""))
        for target in targets:
            if target in name and target not in found:
                found[target] = cls

    lines = [
        "=" * 80,
        "COMPLEXITY TARGETS",
        "=" * 80,
        f"Report: {report_path}",
        "",
    ]

    for target in targets:
        cls = found.get(target)
        if not cls:
            lines.append(f"{target:30} NOT FOUND")
            continue
        comp = int(cls.get("complexity", 0) or 0)
        methods = int(cls.get("methods", 0) or 0)
        module = cls.get("module", "unknown")
        status = "OK" if comp < 50 else "HIGH"
        lines.append(f"{target:30} Complexity: {comp:3} Methods: {methods:2} [{status}] ({module})")

    return lines
