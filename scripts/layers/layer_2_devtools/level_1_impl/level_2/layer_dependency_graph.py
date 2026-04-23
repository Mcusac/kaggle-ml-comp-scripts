#!/usr/bin/env python3
"""
Layer dependency graph generator (bucket-level import adjacency).

Usage (cwd ``kaggle-ml-comp-scripts/scripts/``)::
  python layers/layer_2_devtools/level_1_impl/level_2/layer_dependency_graph.py --help

Writes ``layer_dependency_graph_<date>.md`` under
``<workspace>/.cursor/audit-results/general/audits/`` by default.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

_MODULE = Path(__file__).resolve()
_SCRIPTS = _MODULE.parents[4]


def _load_module_from_path(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load spec for {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_PYMODS = _load_module_from_path(
    "_layer_dep_graph_pymods",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "path"
    / "python_modules.py",
)
_AST_UTILS = _load_module_from_path(
    "_layer_dep_graph_ast_utils",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "parse"
    / "ast"
    / "ast_utils.py",
)
_WORKSPACE = _load_module_from_path(
    "_layer_dep_graph_workspace",
    _SCRIPTS
    / "layers"
    / "layer_2_devtools"
    / "level_0_infra"
    / "level_0"
    / "path"
    / "workspace.py",
)

collect_python_files = _PYMODS.collect_python_files
current_package = _PYMODS.current_package
discover_packages = _PYMODS.discover_packages
file_to_module = _PYMODS.file_to_module
is_internal_module = _PYMODS.is_internal_module

get_imports_from_ast = _AST_UTILS.get_imports_from_ast
parse_file = _AST_UTILS.parse_file

resolve_workspace_root = _WORKSPACE.resolve_workspace_root


@dataclass(frozen=True)
class EdgeExample:
    source_file: str
    import_text: str
    target_module: str


@dataclass(frozen=True)
class GraphSummary:
    files_scanned: int
    parse_error_count: int
    imports_analyzed: int
    bucket_count: int
    edge_pair_count: int
    violation_pair_count: int
    violation_edge_count: int


def _parse_int_suffix(part: str, prefix: str) -> int | None:
    if not part.startswith(prefix):
        return None
    rest = part[len(prefix) :]
    if rest.isdigit():
        return int(rest)
    return None


def _bucket_for_module(module: str) -> str:
    parts = module.split(".")
    if len(parts) < 2:
        return "external_other"

    # General stack: layers.layer_0_core.level_N...
    if parts[:2] == ["layers", "layer_0_core"] and len(parts) >= 3:
        n = _parse_int_suffix(parts[2], "level_")
        if n is not None:
            return f"layer_0_level_{n}"
        return "layer_0_other"

    # Competition infra: layers.layer_1_competition.level_0_infra.level_N...
    if parts[:3] == ["layers", "layer_1_competition", "level_0_infra"] and len(parts) >= 4:
        n = _parse_int_suffix(parts[3], "level_")
        if n is not None:
            return f"competition_infra_level_{n}"
        return "competition_infra_other"

    # Competition impl contests: layers.layer_1_competition.level_1_impl.<slug>.level_K...
    if parts[:3] == ["layers", "layer_1_competition", "level_1_impl"] and len(parts) >= 5:
        slug = parts[3]
        k = _parse_int_suffix(parts[4], "level_")
        if k is not None:
            return f"contest_{slug}_level_{k}"
        return f"contest_{slug}_other"

    # Devtools: layers.layer_2_devtools.level_0_infra.level_M... / level_1_impl.level_M...
    if parts[:2] == ["layers", "layer_2_devtools"] and len(parts) >= 4:
        if parts[2] == "level_0_infra" and parts[3].startswith("level_"):
            m = _parse_int_suffix(parts[3], "level_")
            if m is not None:
                return f"devtools_infra_level_{m}"
            return "devtools_infra_other"
        if parts[2] == "level_1_impl" and parts[3].startswith("level_"):
            m = _parse_int_suffix(parts[3], "level_")
            if m is not None:
                return f"devtools_impl_level_{m}"
            return "devtools_impl_other"
        return "devtools_other"

    # Optional legacy dev scripts
    if parts[0] == "dev":
        return "dev_scripts"

    return "external_other"


def _violation_reason(source_bucket: str, target_bucket: str) -> str | None:
    # layer_0_level_N upward
    if source_bucket.startswith("layer_0_level_") and target_bucket.startswith("layer_0_level_"):
        s = int(source_bucket.rsplit("_", 1)[-1])
        t = int(target_bucket.rsplit("_", 1)[-1])
        if t > s:
            return "upward_layer_0_core"
        return None

    # competition infra upward
    if source_bucket.startswith("competition_infra_level_") and target_bucket.startswith(
        "competition_infra_level_"
    ):
        s = int(source_bucket.rsplit("_", 1)[-1])
        t = int(target_bucket.rsplit("_", 1)[-1])
        if t > s:
            return "upward_competition_infra"
        return None

    # contest slug upward
    if source_bucket.startswith("contest_") and target_bucket.startswith("contest_"):
        # contest_<slug>_level_<k>
        s_parts = source_bucket.split("_")
        t_parts = target_bucket.split("_")
        if len(s_parts) >= 4 and len(t_parts) >= 4 and s_parts[0] == "contest" and t_parts[0] == "contest":
            s_slug = "_".join(s_parts[1:-2])
            t_slug = "_".join(t_parts[1:-2])
            if s_slug == t_slug and s_parts[-2] == "level" and t_parts[-2] == "level":
                s_k = int(s_parts[-1])
                t_k = int(t_parts[-1])
                if t_k > s_k:
                    return "upward_contest_tier"
        return None

    # devtools layering (infra < impl < dev_scripts)
    rank: dict[str, int] = {}
    for m in range(0, 20):
        rank[f"devtools_infra_level_{m}"] = 100 + m
        rank[f"devtools_impl_level_{m}"] = 200 + m
    rank["dev_scripts"] = 1000
    if source_bucket in rank and target_bucket in rank:
        if rank[target_bucket] > rank[source_bucket]:
            return "upward_devtools_layering"
        return None

    return None


def _collect_scan_roots(*, scripts_root: Path, include_dev: bool) -> list[Path]:
    roots: list[Path] = []
    layers_root = scripts_root / "layers"
    if layers_root.is_dir():
        roots.append(layers_root)
    dev_root = scripts_root / "dev"
    if include_dev and dev_root.is_dir():
        roots.append(dev_root)
    return roots


def _build_edges(
    *,
    scripts_root: Path,
    include_dev: bool,
    include_tests: bool,
    max_examples_per_pair: int,
) -> tuple[
    list[str],
    dict[str, dict[str, int]],
    dict[tuple[str, str], list[EdgeExample]],
    dict[tuple[str, str], dict[str, int]],
    dict[tuple[str, str], list[EdgeExample]],
    int,
    int,
    int,
]:
    scan_roots = _collect_scan_roots(scripts_root=scripts_root, include_dev=include_dev)
    internal_packages = discover_packages(scripts_root)

    parse_error_count = 0
    imports_analyzed = 0
    files_scanned = 0

    edge_counts: dict[str, dict[str, int]] = {}
    examples_by_pair: dict[tuple[str, str], list[EdgeExample]] = {}

    violation_counts_by_pair: dict[tuple[str, str], dict[str, int]] = {}
    violation_examples_by_pair: dict[tuple[str, str], list[EdgeExample]] = {}

    def add_example(store: dict[tuple[str, str], list[EdgeExample]], key: tuple[str, str], ex: EdgeExample):
        xs = store.setdefault(key, [])
        xs.append(ex)

    for root in scan_roots:
        for file_path in collect_python_files(root, include_tests=include_tests):
            files_scanned += 1
            source_module = file_to_module(file_path, scripts_root)
            if not source_module:
                continue
            source_bucket = _bucket_for_module(source_module)

            tree = parse_file(file_path)
            if tree is None:
                parse_error_count += 1
                continue

            pkg = current_package(file_path, scripts_root)
            imports = get_imports_from_ast(tree, pkg)
            for target_module in sorted(imports.keys()):
                # Skip non-internal modules for the graph.
                if not is_internal_module(target_module, internal_packages):
                    continue
                imports_analyzed += 1
                target_bucket = _bucket_for_module(target_module)
                edge_counts.setdefault(source_bucket, {})
                edge_counts[source_bucket][target_bucket] = edge_counts[source_bucket].get(target_bucket, 0) + 1

                import_text = f"import {target_module}"
                source_file_rel = file_path.resolve().relative_to(scripts_root.resolve()).as_posix()
                ex = EdgeExample(
                    source_file=source_file_rel,
                    import_text=import_text,
                    target_module=target_module,
                )
                pair = (source_bucket, target_bucket)
                add_example(examples_by_pair, pair, ex)

                reason = _violation_reason(source_bucket, target_bucket)
                if reason:
                    violation_counts_by_pair.setdefault(pair, {})
                    violation_counts_by_pair[pair][reason] = violation_counts_by_pair[pair].get(reason, 0) + 1
                    add_example(violation_examples_by_pair, pair, ex)

    buckets = sorted(set(edge_counts.keys()) | {b for m in edge_counts.values() for b in m.keys()})

    # Deterministic example trimming
    for pair, xs in list(examples_by_pair.items()):
        xs_sorted = sorted(xs, key=lambda e: (e.source_file, e.target_module, e.import_text))
        examples_by_pair[pair] = xs_sorted[: max(0, int(max_examples_per_pair))]
    for pair, xs in list(violation_examples_by_pair.items()):
        xs_sorted = sorted(xs, key=lambda e: (e.source_file, e.target_module, e.import_text))
        violation_examples_by_pair[pair] = xs_sorted[: max(0, int(max_examples_per_pair))]

    return (
        buckets,
        edge_counts,
        examples_by_pair,
        violation_counts_by_pair,
        violation_examples_by_pair,
        files_scanned,
        parse_error_count,
        imports_analyzed,
    )


def _render_markdown(
    *,
    generated: date,
    scripts_root: Path,
    buckets: list[str],
    edge_counts: dict[str, dict[str, int]],
    examples_by_pair: dict[tuple[str, str], list[EdgeExample]],
    violation_counts_by_pair: dict[tuple[str, str], dict[str, int]],
    violation_examples_by_pair: dict[tuple[str, str], list[EdgeExample]],
    summary: GraphSummary,
) -> str:
    lines: list[str] = [
        "---",
        f"generated: {generated.isoformat()}",
        "artifact: layer_dependency_graph",
        "---",
        "",
        "# Layer dependency graph",
        "",
        f"- Scripts root: `{scripts_root.resolve().as_posix()}`",
        f"- Files scanned: {summary.files_scanned}",
        f"- Imports analyzed (internal only): {summary.imports_analyzed}",
        f"- Parse errors: {summary.parse_error_count}",
        f"- Buckets: {summary.bucket_count}",
        f"- Unique bucket edges: {summary.edge_pair_count}",
        f"- Violating bucket edges: {summary.violation_pair_count} (edges counted: {summary.violation_edge_count})",
        "",
        "## Buckets",
        "",
    ]
    for b in buckets:
        lines.append(f"- `{b}`")
    lines.append("")

    lines.append("## Adjacency (bucket -> bucket, count)")
    lines.append("")
    for src in sorted(edge_counts.keys()):
        targets = edge_counts[src]
        if not targets:
            continue
        lines.append(f"### `{src}`")
        for tgt, cnt in sorted(targets.items(), key=lambda kv: (-kv[1], kv[0])):
            lines.append(f"- `{tgt}`: {cnt}")
            pair = (src, tgt)
            xs = examples_by_pair.get(pair, [])
            for ex in xs:
                lines.append(f"  - `{ex.source_file}`: `{ex.import_text}`")
        lines.append("")

    lines.append("## Highlighted edges (potential violations)")
    lines.append("")
    if not violation_counts_by_pair:
        lines.append("- None")
        lines.append("")
        return "\n".join(lines) + "\n"

    for (src, tgt), reasons in sorted(
        violation_counts_by_pair.items(), key=lambda kv: (kv[0][0], kv[0][1])
    ):
        total = sum(reasons.values())
        reason_text = ", ".join(f"{k}={v}" for k, v in sorted(reasons.items()))
        lines.append(f"- `{src}` -> `{tgt}`: {total} ({reason_text})")
        for ex in violation_examples_by_pair.get((src, tgt), []):
            lines.append(f"  - `{ex.source_file}`: `{ex.import_text}`")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> int:
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scripts-root",
        type=Path,
        default=_SCRIPTS,
        help="Scripts root containing layers/ (default: kaggle-ml-comp-scripts/scripts).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Write report here (default: <workspace>/.cursor/audit-results/general/audits).",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="YYYY-MM-DD for filename (default: today).",
    )
    parser.add_argument(
        "--include-dev",
        action="store_true",
        help="Also scan scripts/dev if it exists (default: off).",
    )
    parser.add_argument(
        "--include-tests",
        action="store_true",
        help="Include files matching test_*.py (default: excluded).",
    )
    parser.add_argument(
        "--max-examples",
        type=int,
        default=3,
        help="Max example edges to print per bucket-pair.",
    )
    parser.add_argument(
        "--fail-on-violations",
        action="store_true",
        help="Exit 1 if violation edge count exceeds --max-violations (default 0).",
    )
    parser.add_argument(
        "--max-violations",
        type=int,
        default=0,
        help="When using --fail-on-violations, allow up to this many violating edges.",
    )
    parser.add_argument(
        "--fail-on-parse-errors",
        action="store_true",
        help="Exit 1 if any file failed to parse.",
    )
    args = parser.parse_args()

    scripts_root = args.scripts_root.resolve()
    generated = date.fromisoformat(args.date) if args.date else date.today()
    workspace = resolve_workspace_root(scripts_root)
    output_dir = (
        args.output_dir.resolve()
        if args.output_dir
        else (workspace / ".cursor" / "audit-results" / "general" / "audits")
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    (
        buckets,
        edge_counts,
        examples_by_pair,
        violation_counts_by_pair,
        violation_examples_by_pair,
        files_scanned,
        parse_error_count,
        imports_analyzed,
    ) = _build_edges(
        scripts_root=scripts_root,
        include_dev=bool(args.include_dev),
        include_tests=bool(args.include_tests),
        max_examples_per_pair=int(args.max_examples),
    )

    edge_pair_count = sum(len(m) for m in edge_counts.values())
    violation_pair_count = len(violation_counts_by_pair)
    violation_edge_count = sum(sum(r.values()) for r in violation_counts_by_pair.values())
    summary = GraphSummary(
        files_scanned=files_scanned,
        parse_error_count=parse_error_count,
        imports_analyzed=imports_analyzed,
        bucket_count=len(buckets),
        edge_pair_count=edge_pair_count,
        violation_pair_count=violation_pair_count,
        violation_edge_count=violation_edge_count,
    )

    md = _render_markdown(
        generated=generated,
        scripts_root=scripts_root,
        buckets=buckets,
        edge_counts=edge_counts,
        examples_by_pair=examples_by_pair,
        violation_counts_by_pair=violation_counts_by_pair,
        violation_examples_by_pair=violation_examples_by_pair,
        summary=summary,
    )

    md_path = output_dir / f"layer_dependency_graph_{generated.isoformat()}.md"
    md_path.write_text(md, encoding="utf-8")

    print(f"✅ [OK] Wrote {md_path}")
    print(
        f"[SUMMARY] files={files_scanned} imports={imports_analyzed} parse_errors={parse_error_count} "
        f"buckets={len(buckets)} edges={edge_pair_count} violation_edges={violation_edge_count}"
    )

    exit_code = 0
    if args.fail_on_violations:
        max_v = max(0, int(args.max_violations))
        if violation_edge_count > max_v:
            print(
                f"❌ [FAIL] violation_edge_count={violation_edge_count} exceeds --max-violations={max_v}",
                file=sys.stderr,
            )
            exit_code = 1
    if args.fail_on_parse_errors and parse_error_count > 0:
        print(f"❌ [FAIL] parse_error_count={parse_error_count}", file=sys.stderr)
        exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

