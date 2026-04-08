"""Composed infra-tier scan operations using level_0 primitives."""

import ast
from pathlib import Path

from layers.layer_2_devtools.level_0_infra.level_0.constants.import_patterns import (
    DEEP_LEVEL_RE,
    INFRA_LAYER_IMPORT_RE,
    LEVEL_DIR_RE,
)
from layers.layer_2_devtools.level_0_infra.level_0.models.audit_models import FileReport, Violation
from layers.layer_2_devtools.level_0_infra.level_0.parse.ast.ast_utils import parse_file
from layers.layer_2_devtools.level_0_infra.level_0.path.level_paths import infra_tier_from_level_dir


def scan_infra_file(path: Path, tier_k: int) -> FileReport:
    """Scan one competition infra file and return tier violations."""
    report = FileReport(path=path)
    tree = parse_file(path)
    if tree is None:
        report.parse_error = _read_parse_error(path)
        return report
    is_logic = path.name != "__init__.py"
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        line = getattr(node, "lineno", 0) or 0
        if node.level and node.level > 0:
            if is_logic:
                report.violations.append(_relative_import_violation(node, line))
            continue
        if not node.module:
            continue
        infra_match = INFRA_LAYER_IMPORT_RE.match(node.module)
        if infra_match:
            imported_tier = int(infra_match.group(1))
            if is_logic and imported_tier > tier_k:
                report.violations.append(
                    Violation(
                        "INFRA_TIER_UPWARD",
                        line,
                        f"{node.module!r} (file in infra/level_{tier_k})",
                    )
                )
            continue
        if DEEP_LEVEL_RE.match(node.module):
            if is_logic:
                report.violations.append(
                    Violation("DEEP_PATH", line, f"from {node.module!r} import ...")
                )
            continue
        general_match = LEVEL_DIR_RE.fullmatch(node.module)
        if general_match and is_logic:
            imported = int(general_match.group(1))
            names = ", ".join(alias.name for alias in node.names)
            allowed = imported < tier_k or (tier_k == 0 and imported == 0)
            if not allowed:
                report.violations.append(
                    Violation(
                        "INFRA_GENERAL_LEVEL",
                        line,
                        f"from level_{imported} import {names} "
                        f"(infra/level_{tier_k} may only use lower general levels per scan rules)",
                    )
                )
    return report


def iter_infra_py_files(level_dir: Path) -> list[Path]:
    """Return all Python files under an infra tier directory."""
    if not level_dir.is_dir():
        return []
    return sorted(level_dir.rglob("*.py"))


def scan_infra_level_directory(level_dir: Path) -> list[FileReport]:
    """Scan all Python files in an infra level directory."""
    tier = infra_tier_from_level_dir(level_dir)
    if tier is None:
        return []
    return [scan_infra_file(path, tier) for path in iter_infra_py_files(level_dir)]


def _relative_import_violation(node: ast.ImportFrom, line: int) -> Violation:
    module_name = node.module or ""
    detail = f"relative import (level={node.level})"
    if module_name:
        detail += f" module={module_name!r}"
    return Violation("RELATIVE_IN_LOGIC", line, detail)


def _read_parse_error(path: Path) -> str:
    try:
        source = path.read_text(encoding="utf-8")
        ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return f"line {exc.lineno}: {exc.msg}"
    except OSError as exc:
        return str(exc)
    return "Failed to parse file"


__all__ = ["scan_infra_file", "iter_infra_py_files", "scan_infra_level_directory"]
