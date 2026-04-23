"""Composed contest-tier scan operations using level_0 primitives."""

import ast
from pathlib import Path

from layers.layer_2_devtools.level_0_infra.level_0.constants.import_patterns import (
    CONTEST_LAYER_IMPORT_RE,
    LEVEL_DIR_RE,
)
from layers.layer_2_devtools.level_0_infra.level_0.models.audit_models import FileReport, Violation
from layers.layer_2_devtools.level_0_infra.level_0.parse.ast.ast_utils import parse_file
from layers.layer_2_devtools.level_0_infra.level_0.parse.barrel_names import load_static_barrel_names


def load_level_barrel_names(level_j_dir: Path) -> set[str]:
    """Load static public names from a contest level barrel."""
    return load_static_barrel_names(level_j_dir)


def scan_contest_package_file(
    path: Path,
    contest_slug: str,
    tier_k: int,
    contest_root: Path,
    barrel_cache: dict[int, set[str]] | None = None,
    *,
    forbid_relative_in_logic: bool = True,
    relax_contest_layering: bool = False,
) -> FileReport:
    """Scan one contest package file and return contest-specific violations."""
    report = FileReport(path=path)
    tree = parse_file(path)
    if tree is None:
        report.parse_error = _read_parse_error(path)
        return report
    is_logic = path.name != "__init__.py"
    cache = barrel_cache if barrel_cache is not None else {}

    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        line = getattr(node, "lineno", 0) or 0
        if node.level and node.level > 0:
            if is_logic and forbid_relative_in_logic:
                report.violations.append(_relative_import_violation(node, line))
            continue
        module_name = node.module
        if not module_name:
            continue
        parsed = _parse_contest_layer(module_name)
        if not parsed:
            continue
        source_slug, import_tier, deep_path = parsed
        if source_slug != contest_slug:
            report.violations.append(_other_package_violation(module_name, line, contest_slug))
            continue
        if relax_contest_layering:
            continue
        if is_logic and import_tier >= tier_k:
            report.violations.append(_upward_tier_violation(module_name, line, tier_k))
            continue
        if is_logic and deep_path and import_tier < tier_k:
            imported_names = [alias.name for alias in node.names if alias.name != "*"]
            if not imported_names:
                continue
            if import_tier not in cache:
                cache[import_tier] = load_level_barrel_names(contest_root / f"level_{import_tier}")
            barrel_names = cache[import_tier]
            for name in imported_names:
                if name in barrel_names:
                    report.violations.append(
                        _deep_path_violation(module_name, line, contest_slug, import_tier, name)
                    )
                    break
    return report


def iter_contest_level_py_files(level_dir: Path) -> list[Path]:
    """Return all Python files under one contest level directory."""
    if not level_dir.is_dir():
        return []
    return sorted(level_dir.rglob("*.py"))


def scan_contest_root_directory(
    contest_root: Path,
    contest_slug: str,
    *,
    forbid_relative_in_logic: bool = True,
) -> list[FileReport]:
    """Scan root Python files under one contest package."""
    cache: dict[int, set[str]] = {}
    reports: list[FileReport] = []
    for path in sorted(contest_root.glob("*.py")):
        if not path.is_file():
            continue
        reports.append(
            scan_contest_package_file(
                path,
                contest_slug,
                0,
                contest_root,
                cache,
                forbid_relative_in_logic=forbid_relative_in_logic,
                relax_contest_layering=True,
            )
        )
    return reports


def scan_contest_level_directory(
    contest_root: Path,
    level_dir: Path,
    contest_slug: str,
    *,
    forbid_relative_in_logic: bool = True,
) -> list[FileReport]:
    """Scan all Python files under one contest level directory."""
    match = LEVEL_DIR_RE.fullmatch(level_dir.name)
    if not match:
        return []
    tier = int(match.group(1))
    cache: dict[int, set[str]] = {}
    return [
        scan_contest_package_file(
            path,
            contest_slug,
            tier,
            contest_root,
            cache,
            forbid_relative_in_logic=forbid_relative_in_logic,
        )
        for path in iter_contest_level_py_files(level_dir)
    ]


def _parse_contest_layer(module_name: str) -> tuple[str, int, str | None] | None:
    match = CONTEST_LAYER_IMPORT_RE.match(module_name)
    if not match:
        return None
    return match.group(1), int(match.group(2)), match.group(3)


def _relative_import_violation(node: ast.ImportFrom, line: int) -> Violation:
    module_name = node.module or ""
    detail = f"relative import (level={node.level})"
    if module_name:
        detail += f" module={module_name!r}"
    return Violation("RELATIVE_IN_LOGIC", line, detail)


def _other_package_violation(module_name: str, line: int, contest_slug: str) -> Violation:
    return Violation(
        "CONTEST_OTHER_PACKAGE",
        line,
        f"imports {module_name!r} (scanner scope: {contest_slug})",
    )


def _upward_tier_violation(module_name: str, line: int, tier_k: int) -> Violation:
    return Violation("CONTEST_UPWARD", line, f"{module_name!r} (file under level_{tier_k})")


def _deep_path_violation(
    module_name: str, line: int, contest_slug: str, import_tier: int, name: str
) -> Violation:
    return Violation(
        "CONTEST_DEEP_PATH",
        line,
        f"{module_name!r} import {name!r} — prefer "
        f"layers.layer_1_competition.level_1_impl.{contest_slug}.level_{import_tier} "
        f"barrel if re-exported (heuristic; verify dynamic __all__)",
    )


def _read_parse_error(path: Path) -> str:
    try:
        source = path.read_text(encoding="utf-8")
        ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return f"line {exc.lineno}: {exc.msg}"
    except OSError as exc:
        return str(exc)
    return "Failed to parse file"