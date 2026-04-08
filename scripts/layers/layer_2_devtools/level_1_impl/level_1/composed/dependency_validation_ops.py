"""Dependency validation: scan imports and classify layering violations.

Lives under ``level_1_impl.level_1`` because it composes multiple ``level_0_infra.level_0``
utilities (AST import resolution, workspace discovery) into a workflow; impl sits above infra.
"""

import ast
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_0_infra.level_0.parse.ast.ast_utils import resolve_relative_import
from layers.layer_2_devtools.level_0_infra.level_0.path.workspace import find_workspace_root


@dataclass(frozen=True)
class DependencyEdge:
    source_file: str
    source_bucket: str
    import_text: str
    target_module: str
    target_file: str | None
    target_bucket: str
    violation_type: str | None
    fix_status: str
    notes: str | None = None


def run_dependency_validation_workflow(
    *,
    scripts_root: Path,
    include_dev: bool = True,
    workspace_root: Path | None = None,
    generated: date | None = None,
) -> dict[str, Any]:
    """Build dependency graph, classify violations, and produce report artifacts."""
    root = scripts_root.resolve()
    workspace = workspace_root.resolve() if workspace_root else find_workspace_root(root)
    stamp = generated or date.today()

    search_roots = [root / "layers" / "layer_2_devtools"]
    if include_dev:
        search_roots.append(root / "dev")
    files = _collect_py_files(search_roots)
    module_map = _build_module_map(root, files)

    edges: list[DependencyEdge] = []
    for file_path in files:
        source_bucket = _bucket_for_file(file_path, root)
        source_module = _module_name(root, file_path)
        imports = _extract_imports(file_path, source_module)
        for import_text, target_module in imports:
            target_file = module_map.get(target_module)
            target_bucket = _bucket_for_module(target_module)
            violation_type = _classify_violation(
                source_bucket=source_bucket,
                target_bucket=target_bucket,
                target_module=target_module,
            )
            safe = _is_safe_autofix_candidate(file_path, import_text)
            fix_status = "todo_unsafe_autofix" if violation_type and not safe else "none"
            notes = "barrel_or_export_pattern" if violation_type and not safe else None
            edges.append(
                DependencyEdge(
                    source_file=_rel(workspace, file_path),
                    source_bucket=source_bucket,
                    import_text=import_text,
                    target_module=target_module,
                    target_file=_rel(workspace, target_file) if target_file else None,
                    target_bucket=target_bucket,
                    violation_type=violation_type,
                    fix_status=fix_status,
                    notes=notes,
                )
            )

    by_type = {"same_level": 0, "upward": 0, "illegal_external": 0}
    todo_items: list[dict[str, str]] = []
    for edge in edges:
        if edge.violation_type:
            by_type[edge.violation_type] += 1
            if edge.fix_status.startswith("todo"):
                todo_items.append(
                    {
                        "source_file": edge.source_file,
                        "import_text": edge.import_text,
                        "target_module": edge.target_module,
                        "reason": edge.notes or "unsafe",
                    }
                )

    report = {
        "generated": stamp.isoformat(),
        "workspace": workspace.as_posix(),
        "files_scanned": len(files),
        "imports_analyzed": len(edges),
        "violations": {
            "same_level": by_type["same_level"],
            "upward": by_type["upward"],
            "illegal_external": by_type["illegal_external"],
            "total": sum(by_type.values()),
        },
        "violations_fixed": 0,
        "todos": todo_items,
        "edges": [edge.__dict__ for edge in edges],
    }
    report["markdown"] = _build_markdown_summary(report)
    return report


def write_dependency_report_artifacts(
    report: dict[str, Any],
    *,
    workspace: Path,
    output_base: Path | None = None,
) -> tuple[Path, Path]:
    """Write deterministic JSON + markdown dependency report artifacts."""
    base = (
        output_base
        if output_base is not None
        else workspace
        / ".cursor"
        / "audit-results"
        / "general"
        / "summaries"
        / f"dependency_validation_{report['generated']}"
    )
    base.parent.mkdir(parents=True, exist_ok=True)
    json_path = Path(str(base) + ".json")
    md_path = Path(str(base) + ".md")
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(report["markdown"], encoding="utf-8")
    return json_path, md_path


def _is_under_impl_tests(path: Path) -> bool:
    parts = path.parts
    if any(
        parts[i] == "level_1_impl" and parts[i + 1] == "tests"
        for i in range(len(parts) - 1)
    ):
        return True
    return any(
        parts[i] == "impl" and parts[i + 1] == "tests" for i in range(len(parts) - 1)
    )


def _collect_py_files(roots: list[Path]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            if _is_under_impl_tests(path):
                continue
            files.append(path.resolve())
    return sorted(files)


def _module_name(scripts_root: Path, file_path: Path) -> str:
    rel = file_path.resolve().relative_to(scripts_root.resolve())
    parts = list(rel.parts)
    parts[-1] = parts[-1].removesuffix(".py")
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def _build_module_map(scripts_root: Path, files: list[Path]) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for file_path in files:
        out[_module_name(scripts_root, file_path)] = file_path
    return out


def _extract_imports(file_path: Path, current_module: str) -> list[tuple[str, str]]:
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(file_path))
    imports: list[tuple[str, str]] = []
    current_pkg = current_module.rsplit(".", 1)[0] if "." in current_module else ""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((f"import {alias.name}", alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                resolved = resolve_relative_import(node.level, current_pkg, node.module)
            else:
                resolved = node.module
            if resolved:
                imports.append((f"from {'.' * node.level}{node.module or ''} import ...", resolved))
    return imports


def _bucket_for_file(file_path: Path, scripts_root: Path) -> str:
    return _bucket_for_module(_module_name(scripts_root, file_path))


def _bucket_for_module(module: str) -> str:
    if module.startswith("layers.layer_2_devtools.level_0_infra.level_0"):
        return "infra_level_0"
    if module.startswith("layers.layer_2_devtools.level_0_infra.level_1"):
        return "infra_level_1"
    if module.startswith("layers.layer_2_devtools.level_0_infra.level_2"):
        return "infra_level_2"
    if module.startswith("layers.layer_2_devtools.level_1_impl.level_0"):
        return "impl_level_0"
    if module.startswith("layers.layer_2_devtools.level_1_impl.level_1"):
        return "impl_level_1"
    if module.startswith("dev."):
        return "scripts_dev"
    return "external_other"


def _infra_disallowed_layers_target(source_bucket: str, target_module: str) -> bool:
    """Infra may use ``layers.layer_0_core`` and ``layers.layer_2_devtools.level_0_infra`` only."""
    if source_bucket not in ("infra_level_0", "infra_level_1", "infra_level_2"):
        return False
    if not target_module.startswith("layers."):
        return False
    if target_module.startswith("layers.layer_0_core"):
        return False
    if target_module == "layers.layer_2_devtools.level_0_infra" or target_module.startswith(
        "layers.layer_2_devtools.level_0_infra."
    ):
        return False
    return True


def _classify_violation(
    *,
    source_bucket: str,
    target_bucket: str,
    target_module: str,
) -> str | None:
    if _infra_disallowed_layers_target(source_bucket, target_module):
        return "illegal_external"

    layered = {
        "infra_level_0": 0,
        "infra_level_1": 1,
        "infra_level_2": 2,
        "impl_level_0": 3,
        "impl_level_1": 4,
        "scripts_dev": 5,
    }
    if source_bucket in layered and target_bucket in layered:
        if source_bucket == target_bucket:
            return None
        if layered[target_bucket] > layered[source_bucket]:
            return "upward"
    if source_bucket in layered and target_module.startswith("layers.") and not (
        target_module.startswith("layers.layer_2_devtools")
        or target_module.startswith("layers.layer_0_core")
    ):
        return "illegal_external"
    return None


def _is_safe_autofix_candidate(file_path: Path, import_text: str) -> bool:
    if file_path.name == "__init__.py":
        return False
    text = file_path.read_text(encoding="utf-8")
    if "import *" in text or "__all__" in text:
        return False
    if "import ..." in import_text and import_text.startswith("from ."):
        return False
    return True


def _rel(workspace: Path, path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(workspace.resolve()).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _build_markdown_summary(report: dict[str, Any]) -> str:
    violations = report["violations"]
    lines = [
        "---",
        f"generated: {report['generated']}",
        "artifact: dependency_validation",
        "---",
        "",
        "# Dependency Validation Report",
        "",
        f"- Files scanned: {report['files_scanned']}",
        f"- Imports analyzed: {report['imports_analyzed']}",
        f"- Total violations: {violations['total']}",
        f"- Same-level: {violations['same_level']}",
        f"- Upward: {violations['upward']}",
        f"- Illegal external: {violations['illegal_external']}",
        f"- Violations fixed: {report['violations_fixed']}",
        "",
        "## Remaining TODOs",
        "",
    ]
    todos = report.get("todos", [])
    if not todos:
        lines.append("- None")
    else:
        for todo in todos:
            lines.append(
                f"- `{todo['source_file']}`: {todo['import_text']} -> "
                f"`{todo['target_module']}` ({todo['reason']})"
            )
    lines.append("")
    return "\n".join(lines)


__all__ = [
    "DependencyEdge",
    "run_dependency_validation_workflow",
    "write_dependency_report_artifacts",
]
