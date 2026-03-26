"""Dependency rule analyzer: components must not import contest/orchestration; core must not import components/orchestration/contest."""

import ast
from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_0_infra.level_0 import(
    BaseAnalyzer,
    collect_python_files,
    current_package,
    parse_file,
    resolve_relative_import,
)


def _get_imports_with_lines(file_path: Path, current_pkg: str) -> list[tuple[int, str]]:
    """Return list of (line_number, absolute_module_name) for every import in the file."""
    tree = parse_file(file_path)
    if tree is None:
        return []

    result: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                result.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            level = getattr(node, "level", 0)
            resolved = (
                (resolve_relative_import(level, current_pkg, node.module) or "")
                if level >= 1
                else (node.module or "")
            )
            if resolved:
                result.append((node.lineno, resolved))
    return result


class DependencyRuleAnalyzer(BaseAnalyzer):
    """
    Enforce dependency rules:
    - Components must not import from contest or orchestration.
    - Core must not import from components, orchestration, or contest.
    """

    FORBIDDEN_FOR_COMPONENTS = ("contest", "orchestration")
    FORBIDDEN_FOR_CORE = ("components", "orchestration", "contest")

    @property
    def name(self) -> str:
        return "dependency_rule"

    def analyze(self) -> dict[str, Any]:
        violations: list[dict[str, Any]] = []

        components_dir = self.root / "components"
        core_dir = self.root / "core"

        if components_dir.is_dir():
            files = collect_python_files(components_dir)
            for file_path in files:
                rel_path = file_path.relative_to(self.root)
                current_pkg = current_package(file_path, self.root)
                for line_no, mod in _get_imports_with_lines(file_path, current_pkg):
                    top = mod.split(".")[0] if mod else ""
                    if top in self.FORBIDDEN_FOR_COMPONENTS:
                        violations.append({
                            "file": str(rel_path),
                            "line": line_no,
                            "module": mod,
                            "rule": "components must not import contest or orchestration",
                        })

        if core_dir.is_dir():
            files = collect_python_files(core_dir)
            for file_path in files:
                rel_path = file_path.relative_to(self.root)
                current_pkg = current_package(file_path, self.root)
                for line_no, mod in _get_imports_with_lines(file_path, current_pkg):
                    top = mod.split(".")[0] if mod else ""
                    if top in self.FORBIDDEN_FOR_CORE:
                        violations.append({
                            "file": str(rel_path),
                            "line": line_no,
                            "module": mod,
                            "rule": "core must not import components, orchestration, or contest",
                        })

        return {
            "violations": violations,
            "passed": len(violations) == 0,
        }
