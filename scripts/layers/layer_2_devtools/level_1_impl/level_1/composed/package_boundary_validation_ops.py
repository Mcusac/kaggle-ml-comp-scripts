"""Package boundary validation workflow (scan + matrix + artifacts)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_0_infra.level_0.path.python_modules import (
    discover_packages,
    is_internal_module,
)
from layers.layer_2_devtools.level_0_infra.level_0.path.workspace import find_workspace_root
from layers.layer_2_devtools.level_0_infra.level_0.validation.boundaries import (
    PackageBoundarySpec,
    classify_module_to_boundary,
)
from layers.layer_2_devtools.level_1_impl.level_1.composed.import_scan_ops import (
    ScannedImport,
    build_module_map,
    collect_py_files,
    module_name,
    extract_imports,
)


@dataclass(frozen=True)
class BoundaryEdge:
    source_file: str
    source_module: str
    source_node: str
    import_text: str
    target_module: str
    target_file: str | None
    target_node: str
    violation_type: str | None
    reason: str | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_file": self.source_file,
            "source_module": self.source_module,
            "source_node": self.source_node,
            "import_text": self.import_text,
            "target_module": self.target_module,
            "target_file": self.target_file,
            "target_node": self.target_node,
            "violation_type": self.violation_type,
            "reason": self.reason,
        }


def _rel(workspace: Path, path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(workspace.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _default_scan_roots(*, scripts_root: Path, include_dev: bool) -> list[Path]:
    roots: list[Path] = []
    layers_root = scripts_root / "layers"
    if layers_root.is_dir():
        roots.append(layers_root)
    dev_root = scripts_root / "dev"
    if include_dev and dev_root.is_dir():
        roots.append(dev_root)
    return roots


def _filter_under_scope(*, files: list[Path], scope_root: Path | None) -> list[Path]:
    if scope_root is None:
        return files
    sr = scope_root.resolve()
    out: list[Path] = []
    for p in files:
        try:
            p.resolve().relative_to(sr)
            out.append(p)
        except ValueError:
            continue
    return out


def run_package_boundary_validation_workflow(
    *,
    scripts_root: Path,
    include_dev: bool = True,
    workspace_root: Path | None = None,
    scope_root: Path | None = None,
    generated: date | None = None,
    max_examples_per_pair: int = 3,
) -> dict[str, Any]:
    root = scripts_root.resolve()
    workspace = workspace_root.resolve() if workspace_root else find_workspace_root(root)
    stamp = generated or date.today()

    scan_roots = _default_scan_roots(scripts_root=root, include_dev=include_dev)
    files = collect_py_files(roots=scan_roots)
    files = _filter_under_scope(files=files, scope_root=scope_root)

    module_map = build_module_map(scripts_root=root, files=files)
    internal_packages = discover_packages(root)

    spec = PackageBoundarySpec()

    nodes: dict[str, dict[str, object]] = {}
    edge_counts: dict[str, dict[str, int]] = {}
    violation_counts: dict[str, int] = {"upward": 0, "illegal_external": 0, "total": 0}
    examples_by_pair: dict[tuple[str, str], list[dict[str, str]]] = {}

    edges: list[BoundaryEdge] = []

    def ensure_node(mod: str) -> tuple[str, Any]:
        c = classify_module_to_boundary(mod)
        if c.node is None:
            return "out_of_scope", c
        if c.node.key not in nodes:
            nodes[c.node.key] = {"key": c.node.key, "label": c.node.label, "sort_key": list(c.node.sort_key)}
        return c.node.key, c

    for file_path in files:
        src_mod = module_name(scripts_root=root, file_path=file_path)
        src_node_key, src_cls = ensure_node(src_mod)
        if src_node_key == "out_of_scope":
            continue

        scanned: list[ScannedImport]
        try:
            scanned = extract_imports(file_path=file_path, current_module=src_mod)
        except (OSError, SyntaxError, UnicodeError):
            # Keep boundary scan robust; parse errors are tracked by other tools.
            continue

        for imp in scanned:
            if not is_internal_module(imp.target_module, internal_packages):
                continue

            tgt_node_key, tgt_cls = ensure_node(imp.target_module)
            if tgt_node_key == "out_of_scope":
                continue

            decision = spec.decide(source=src_cls, target=tgt_cls, target_module=imp.target_module)
            vt = decision.violation_type

            edge_counts.setdefault(src_node_key, {})
            edge_counts[src_node_key][tgt_node_key] = edge_counts[src_node_key].get(tgt_node_key, 0) + 1

            if vt:
                violation_counts["total"] += 1
                if vt in violation_counts:
                    violation_counts[vt] += 1
                else:
                    violation_counts[vt] = 1

                pair = (src_node_key, tgt_node_key)
                xs = examples_by_pair.setdefault(pair, [])
                xs.append(
                    {
                        "source_file": _rel(workspace, file_path) or "",
                        "import_text": imp.import_text,
                        "target_module": imp.target_module,
                    }
                )

            edges.append(
                BoundaryEdge(
                    source_file=_rel(workspace, file_path) or "",
                    source_module=src_mod,
                    source_node=src_node_key,
                    import_text=imp.import_text,
                    target_module=imp.target_module,
                    target_file=_rel(workspace, module_map.get(imp.target_module)),
                    target_node=tgt_node_key,
                    violation_type=vt,
                    reason=decision.reason,
                )
            )

    # Deterministic example trimming
    for pair, xs in list(examples_by_pair.items()):
        xs_sorted = sorted(xs, key=lambda d: (d.get("source_file", ""), d.get("target_module", ""), d.get("import_text", "")))
        examples_by_pair[pair] = xs_sorted[: max(0, int(max_examples_per_pair))]

    nodes_sorted = sorted(nodes.values(), key=lambda d: tuple(d.get("sort_key", [])))
    node_keys = [d["key"] for d in nodes_sorted]

    report: dict[str, Any] = {
        "generated": stamp.isoformat(),
        "workspace": workspace.as_posix(),
        "scripts_root": root.as_posix(),
        "scope_root": scope_root.resolve().as_posix() if scope_root else None,
        "files_scanned": len(files),
        "nodes": nodes_sorted,
        "node_keys": node_keys,
        "edge_counts": edge_counts,
        "violations": violation_counts,
        "examples_by_pair": {
            f"{k[0]}::{k[1]}": v for k, v in sorted(examples_by_pair.items(), key=lambda kv: (kv[0][0], kv[0][1]))
        },
        "edges": [e.to_dict() for e in edges],
    }
    report["markdown"] = build_boundary_markdown(report)
    return report


def build_boundary_markdown(report: dict[str, Any]) -> str:
    nodes: list[dict[str, Any]] = list(report.get("nodes", []))
    node_keys: list[str] = list(report.get("node_keys", []))
    edge_counts: dict[str, dict[str, int]] = dict(report.get("edge_counts", {}))
    violations: dict[str, int] = dict(report.get("violations", {}))
    examples_by_pair: dict[str, list[dict[str, str]]] = dict(report.get("examples_by_pair", {}))

    label_by_key = {n.get("key"): n.get("label") for n in nodes}

    lines: list[str] = [
        "---",
        f"generated: {report.get('generated')}",
        "artifact: package_boundary_validation",
        "---",
        "",
        "# Package Boundary Validation Report",
        "",
        f"- Scripts root: `{report.get('scripts_root')}`",
        f"- Scope root: `{report.get('scope_root')}`" if report.get("scope_root") else "- Scope root: (none; full scan)",
        f"- Files scanned: {report.get('files_scanned')}",
        f"- Violations: {violations.get('total', 0)} (upward={violations.get('upward', 0)} illegal_external={violations.get('illegal_external', 0)})",
        "",
        "## Nodes",
        "",
    ]
    for k in node_keys:
        lines.append(f"- `{k}`: {label_by_key.get(k, '')}")
    lines.append("")

    lines.append("## Boundary matrix (counts; only observed internal edges)")
    lines.append("")
    header = ["source\\target"] + [f"`{k}`" for k in node_keys]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("| " + " | ".join(["---"] * len(header)) + " |")
    for src in node_keys:
        row = [f"`{src}`"]
        targets = edge_counts.get(src, {})
        for tgt in node_keys:
            cnt = int(targets.get(tgt, 0))
            row.append(str(cnt) if cnt else "")
        lines.append("| " + " | ".join(row) + " |")
    lines.append("")

    lines.append("## Violating pairs (examples)")
    lines.append("")
    if not examples_by_pair:
        lines.append("- None")
        lines.append("")
        return "\n".join(lines) + "\n"

    for pair_key, xs in examples_by_pair.items():
        src, tgt = pair_key.split("::", 1)
        lines.append(f"- `{src}` -> `{tgt}`")
        for ex in xs:
            lines.append(f"  - `{ex.get('source_file', '')}`: `{ex.get('import_text', '')}` -> `{ex.get('target_module', '')}`")
    lines.append("")
    return "\n".join(lines) + "\n"


def write_package_boundary_report_artifacts(
    report: dict[str, Any],
    *,
    workspace: Path,
    output_base: Path | None = None,
) -> tuple[Path, Path]:
    base = (
        output_base
        if output_base is not None
        else workspace
        / ".cursor"
        / "audit-results"
        / "general"
        / "summaries"
        / f"package_boundary_validation_{report['generated']}"
    )
    base.parent.mkdir(parents=True, exist_ok=True)
    json_path = Path(str(base) + ".json")
    md_path = Path(str(base) + ".md")
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(str(report.get("markdown", "")), encoding="utf-8")
    return json_path, md_path

