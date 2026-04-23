"""Composed general-stack scan operations using level_0 primitives."""

import ast
import re
from datetime import date
from pathlib import Path

from layers.layer_2_devtools.level_0_infra.level_0.models.audit_models import FileReport, Violation
from layers.layer_2_devtools.level_0_infra.level_0.constants.import_patterns import LEVEL_DIR_RE
from layers.layer_2_devtools.level_0_infra.level_0.path.level_paths import file_level_from_path
from layers.layer_2_devtools.level_0_infra.level_0.parse.ast.ast_utils import parse_file
from layers.layer_2_devtools.level_0_infra.level_0.validation.import_rules.general_rules import (
    classify_general_import_from,
    has_deep_level_path,
)

_LAYER0_CORE_PREFIX = "layers.layer_0_core."


def scan_general_stack_file(path: Path, scripts_dir: Path) -> FileReport:
    """Scan a general-stack file and return import-layer violations."""
    report = FileReport(path=path)
    current_level = file_level_from_path(path, scripts_dir)
    if current_level is None:
        return report
    tree = parse_file(path)
    if tree is None:
        report.parse_error = _read_parse_error(path)
        return report
    is_logic = path.name != "__init__.py"
    uses_explicit_l0_core = _file_uses_explicit_layer0_core(tree)
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        line = getattr(node, "lineno", 0) or 0
        if node.level and node.level > 0:
            if is_logic:
                report.violations.append(
                    _build_relative_import_violation(node, line, file_level=current_level)
                )
            continue
        module_name = node.module
        if not module_name:
            continue
        if (
            uses_explicit_l0_core
            and is_logic
            and LEVEL_DIR_RE.fullmatch(module_name)
        ):
            names = ", ".join(alias.name for alias in node.names)
            report.violations.append(
                Violation(
                    "LAYER0_CORE_MIXED_IMPORT_STYLE",
                    line,
                    f"from {module_name} import {names} — with explicit "
                    f"`{_LAYER0_CORE_PREFIX}...` imports in this file, use "
                    f"`from layers.layer_0_core.{module_name} import ...` "
                    f"(python-import-surfaces.mdc: framework-core explicit imports).",
                    file_level=current_level,
                )
            )
            continue
        if has_deep_level_path(module_name):
            if is_logic:
                m = re.match(r"^level_(\d+)\.", module_name)
                implied = int(m.group(1)) if m else None
                sug = implied + 1 if implied is not None else None
                report.violations.append(
                    Violation(
                        "DEEP_PATH",
                        line,
                        f"from {module_name!r} import ...",
                        file_level=current_level,
                        imported_level=implied,
                        suggested_min_level=sug,
                    )
                )
            continue
        classification = classify_general_import_from(module_name, current_level)
        if classification and is_logic:
            names = ", ".join(alias.name for alias in node.names)
            report.violations.append(
                _build_level_violation(classification, line, current_level, names)
            )
    return report


def _file_uses_explicit_layer0_core(tree: ast.Module) -> bool:
    """True if the module has any ``from layers.layer_0_core.... import``."""
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ImportFrom)
            and node.module
            and str(node.module).startswith(_LAYER0_CORE_PREFIX)
        ):
            return True
    return False


def iter_level_py_files(scripts_dir: Path) -> list[Path]:
    """Return all Python files under level_0..level_10 roots."""
    files: list[Path] = []
    for level in range(0, 11):
        root = scripts_dir / f"level_{level}"
        if root.is_dir():
            files.extend(sorted(root.rglob("*.py")))
    return files


def build_general_markdown(
    reports: list[FileReport],
    generated: date,
    scripts_dir: Path,
    workspace: Path,
) -> str:
    """Build markdown summary for general-stack scan output."""
    lines = [
        "---",
        f"generated: {generated.isoformat()}",
        "scope: general",
        "artifact: level_violations_scan",
        "---",
        "",
        "# Level import violations scan",
        "",
        f"**Scripts root:** `{scripts_dir.as_posix()}`",
        "",
        "## Summary",
        "",
    ]
    kinds_order = [
        "LAYER0_CORE_MIXED_IMPORT_STYLE",
        "WRONG_LEVEL",
        "UPWARD",
        "DEEP_PATH",
        "RELATIVE_IN_LOGIC",
        "PARSE_ERROR",
    ]
    for kind in kinds_order:
        count = _count_kind(reports, kind)
        lines.append(f"- **{kind}:** {count} file(s)")
    lines.append("")
    lines.extend(_build_violation_sections(reports, workspace, kinds_order))
    lines.append("## Files with no violations in this scan")
    lines.append("")
    clean = [report for report in reports if not report.parse_error and not report.violations]
    if not clean:
        lines.append("_None (every file had at least one issue or parse error)._")
    else:
        for report in sorted(clean, key=lambda item: str(item.path)):
            rel = report.path.relative_to(workspace)
            lines.append(f"- `{rel.as_posix()}`")
    lines.append("")
    return "\n".join(lines)


def build_general_json_payload(
    reports: list[FileReport],
    generated: date,
    scripts_dir: Path,
    workspace: Path,
) -> dict:
    """Build normalized JSON payload for general-stack scan output."""
    violations: list[dict] = []
    parse_errors: list[dict] = []
    for report in reports:
        rel_file = report.path.relative_to(workspace).as_posix()
        if report.parse_error:
            parse_errors.append({"file": rel_file, "detail": report.parse_error})
            continue
        for violation in report.violations:
            entry: dict = {
                "file": rel_file,
                "kind": violation.kind,
                "line": violation.line,
                "detail": violation.detail,
            }
            if violation.file_level is not None:
                entry["file_level"] = violation.file_level
            if violation.imported_level is not None:
                entry["imported_level"] = violation.imported_level
            if violation.suggested_min_level is not None:
                entry["suggested_min_level"] = violation.suggested_min_level
            violations.append(entry)
    return {
        "generated": generated.isoformat(),
        "scope": "general",
        "artifact": "level_violations_scan",
        "schema": "level_violations_scan.v2",
        "scripts_dir": str(scripts_dir.resolve()),
        "violations": violations,
        "parse_errors": parse_errors,
    }


def _build_relative_import_violation(node: object, line: int, *, file_level: int) -> Violation:
    module_name = getattr(node, "module", "") or ""
    level = getattr(node, "level", 0)
    detail = f"relative import (level={level})"
    if module_name:
        detail += f" module={module_name!r}"
    return Violation("RELATIVE_IN_LOGIC", line, detail, file_level=file_level)


def _suggested_min_level_for_level_import(*, imported_level: int) -> int:
    """A logic file that uses ``from level_I import`` must live under at least level_(I+1)."""
    return imported_level + 1


def _build_level_violation(
    classification: tuple[str, int], line: int, current_level: int, names: str
) -> Violation:
    kind, imported_level = classification
    sug = _suggested_min_level_for_level_import(imported_level=imported_level)
    if kind == "WRONG_LEVEL":
        return Violation(
            "WRONG_LEVEL",
            line,
            f"from level_{current_level} import {names}",
            file_level=current_level,
            imported_level=imported_level,
            suggested_min_level=sug,
        )
    return Violation(
        "UPWARD",
        line,
        f"from level_{imported_level} import {names} (file under level_{current_level})",
        file_level=current_level,
        imported_level=imported_level,
        suggested_min_level=sug,
    )


def _count_kind(reports: list[FileReport], kind: str) -> int:
    if kind == "PARSE_ERROR":
        return sum(1 for report in reports if report.parse_error)
    return sum(1 for report in reports if any(v.kind == kind for v in report.violations))


def _build_violation_sections(
    reports: list[FileReport], workspace: Path, kinds_order: list[str]
) -> list[str]:
    lines: list[str] = []
    for kind in kinds_order:
        if kind == "PARSE_ERROR":
            bad = [report for report in reports if report.parse_error]
            if not bad:
                continue
            lines.append(f"## {kind}")
            lines.append("")
            for report in sorted(bad, key=lambda item: str(item.path)):
                rel = report.path.relative_to(workspace)
                lines.append(f"- `{rel.as_posix()}` — {report.parse_error}")
            lines.append("")
            continue
        files_with = [report for report in reports if any(v.kind == kind for v in report.violations)]
        if not files_with:
            continue
        lines.append(f"## {kind}")
        lines.append("")
        for report in sorted(files_with, key=lambda item: str(item.path)):
            rel = report.path.relative_to(workspace)
            violations = [v for v in report.violations if v.kind == kind]
            lines.append(f"### `{rel.as_posix()}`")
            lines.append("")
            for violation in violations:
                lines.append(f"- Line {violation.line}: {violation.detail}")
            lines.append("")
    return lines


def _read_parse_error(path: Path) -> str:
    try:
        source = path.read_text(encoding="utf-8")
        ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return f"line {exc.lineno}: {exc.msg}"
    except OSError as exc:
        return str(exc)
    return "Failed to parse file"