"""Composed special-tree scan operations using level_0 primitives."""

import ast
from pathlib import Path

from layers.layer_2_devtools.level_0_infra.level_0.models.audit_models import FileReport, Violation
from layers.layer_2_devtools.level_0_infra.level_0.parse.ast.ast_utils import parse_file


def scan_special_tree_file(path: Path) -> FileReport:
    """Scan one non-tier file for relative-import violations."""
    report = FileReport(path=path)
    tree = parse_file(path)
    if tree is None:
        report.parse_error = _read_parse_error(path)
        return report
    is_logic = path.name != "__init__.py"
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        if node.level and node.level > 0 and is_logic:
            line = getattr(node, "lineno", 0) or 0
            module_name = node.module or ""
            detail = f"relative import (level={node.level})"
            if module_name:
                detail += f" module={module_name!r}"
            report.violations.append(Violation("RELATIVE_IN_LOGIC", line, detail))
    return report


def iter_special_py_files(root: Path) -> list[Path]:
    """Return all Python files under a non-tier tree root."""
    if not root.is_dir():
        return []
    return sorted(root.rglob("*.py"))


def scan_special_tree_directory(root: Path) -> list[FileReport]:
    """Scan all Python files under a non-tier tree root."""
    return [scan_special_tree_file(path) for path in iter_special_py_files(root)]


def _read_parse_error(path: Path) -> str:
    try:
        source = path.read_text(encoding="utf-8")
        ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return f"line {exc.lineno}: {exc.msg}"
    except OSError as exc:
        return str(exc)
    return "Failed to parse file"