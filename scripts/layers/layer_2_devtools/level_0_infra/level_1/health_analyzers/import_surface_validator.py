"""Import surface validator for strict import path policy.

This analyzer is intentionally filesystem- and AST-based (no runtime importing).
It enforces the general-stack rules in `python-import-surfaces.mdc` for trees that
contain `level_0/ .. level_N/` directories (e.g. `layer_0_core`).
"""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_0_infra.level_0.base_health_analyzer import BaseAnalyzer
from layers.layer_2_devtools.level_0_infra.level_0.path.python_modules import (
    collect_python_files,
    current_package,
    discover_packages,
    file_to_module,
    is_internal_module,
    module_exists,
)
from layers.layer_2_devtools.level_0_infra.level_0.parse.ast.ast_utils import (
    get_imports_from_ast,
    parse_file,
    resolve_relative_import,
)
from layers.layer_2_devtools.level_0_infra.level_0.validation.import_rules.general_rules import (
    classify_general_import_from,
    has_deep_level_path,
)


@dataclass(frozen=True)
class ImportViolation:
    file: str
    line: int
    kind: str
    module: str
    name: str | None
    message: str
    suggested: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file,
            "line": int(self.line),
            "kind": self.kind,
            "module": self.module,
            "name": self.name,
            "message": self.message,
            "suggested": self.suggested,
        }


def _find_general_level(rel_parts: tuple[str, ...]) -> int | None:
    """Return level_N integer if path is under `level_N/`, else None."""
    if not rel_parts:
        return None
    head = rel_parts[0]
    if not head.startswith("level_"):
        return None
    tail = head[6:]
    if not tail.isdigit():
        return None
    return int(tail)


def _extract_from_import_names(node: ast.ImportFrom) -> list[str]:
    out: list[str] = []
    for alias in getattr(node, "names", []):
        name = getattr(alias, "name", None)
        if isinstance(name, str) and name and name != "*":
            out.append(name)
    return out


def _exported_names_from_init(init_py: Path) -> set[str]:
    """Conservative export discovery for __init__.py.

    Supports:
    - __all__ assignments with a tuple/list of string literals
    - `from .mod import X` / `from .mod import X as Y` re-exports (collect alias/asname)
    """
    tree = parse_file(init_py)
    if tree is None:
        return set()

    exports: set[str] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for tgt in node.targets:
                if isinstance(tgt, ast.Name) and tgt.id == "__all__":
                    val = node.value
                    if isinstance(val, (ast.Tuple, ast.List)):
                        for elt in val.elts:
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                                exports.add(elt.value)
        elif isinstance(node, ast.ImportFrom):
            level = getattr(node, "level", 0)
            if level >= 1:
                # relative re-export inside package init
                for alias in getattr(node, "names", []):
                    name = getattr(alias, "name", None)
                    asname = getattr(alias, "asname", None)
                    if isinstance(name, str) and name and name != "*":
                        exports.add(str(asname or name))
    return exports


class ImportSurfaceValidator(BaseAnalyzer):
    """Validate strict general-stack import surfaces and module existence."""

    def __init__(self, root: Path, include_tests: bool = False):
        super().__init__(root)
        self._include_tests = bool(include_tests)

    @property
    def name(self) -> str:
        return "import_surface"

    def analyze(self) -> dict[str, Any]:
        files = collect_python_files(self.root, include_tests=self._include_tests)
        internal_packages = discover_packages(self.root)

        violations: list[ImportViolation] = []
        parse_error_count = 0

        export_cache: dict[Path, set[str]] = {}

        for file_path in files:
            rel = file_path.resolve().relative_to(self.root.resolve())
            rel_parts = tuple(rel.parts)
            current_level = _find_general_level(rel_parts)
            module_name = file_to_module(file_path, self.root) or rel.as_posix()

            tree = parse_file(file_path)
            if tree is None:
                parse_error_count += 1
                continue

            pkg = current_package(file_path, self.root)

            # (A) Policy: forbid relative imports in non-__init__.py logic files.
            for node in ast.walk(tree):
                if not isinstance(node, ast.ImportFrom):
                    continue
                level = getattr(node, "level", 0)
                if level >= 1 and file_path.name != "__init__.py":
                    resolved = resolve_relative_import(level, pkg, node.module)
                    violations.append(
                        ImportViolation(
                            file=module_name,
                            line=int(getattr(node, "lineno", 0) or 0),
                            kind="RELATIVE_IN_LOGIC",
                            module=resolved or "",
                            name=None,
                            message="Relative imports are only allowed in __init__.py files.",
                            suggested=None,
                        )
                    )

            # (B) General-stack: detect deep level_N imports and wrong/upward with real line numbers.
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported_mod = getattr(alias, "name", "") or ""
                        if not imported_mod:
                            continue
                        self._validate_import_target(
                            violations=violations,
                            module_name=module_name,
                            lineno=int(getattr(node, "lineno", 0) or 0),
                            imported_mod=imported_mod,
                            current_level=current_level,
                            internal_packages=internal_packages,
                        )
                elif isinstance(node, ast.ImportFrom):
                    level = getattr(node, "level", 0)
                    if level >= 1:
                        imported_mod = resolve_relative_import(level, pkg, node.module) or ""
                    else:
                        imported_mod = str(node.module or "")
                    if not imported_mod:
                        continue
                    self._validate_import_target(
                        violations=violations,
                        module_name=module_name,
                        lineno=int(getattr(node, "lineno", 0) or 0),
                        imported_mod=imported_mod,
                        current_level=current_level,
                        internal_packages=internal_packages,
                    )

            # (C) Phase-2 suggestions: when deep import can be replaced by barrel import.
            for node in ast.walk(tree):
                if not isinstance(node, ast.ImportFrom):
                    continue
                if getattr(node, "level", 0) >= 1:
                    continue
                base = node.module
                if not isinstance(base, str) or not has_deep_level_path(base):
                    continue
                if not is_internal_module(base, internal_packages):
                    continue

                # infer level_N from module path
                head = base.split(".", 1)[0]
                if not head.startswith("level_") or not head[6:].isdigit():
                    continue
                barrel = head
                init_py = self.root / barrel / "__init__.py"
                if not init_py.is_file():
                    continue

                if init_py not in export_cache:
                    export_cache[init_py] = _exported_names_from_init(init_py)
                exported = export_cache[init_py]

                for sym in _extract_from_import_names(node):
                    if sym in exported:
                        violations.append(
                            ImportViolation(
                                file=module_name,
                                line=int(getattr(node, "lineno", 0) or 0),
                                kind="DEEP_LEVEL_PATH_CANONICAL",
                                module=base,
                                name=sym,
                                message="Deep import can be replaced by barrel import per __init__.py exports.",
                                suggested=f"from {barrel} import {sym}",
                            )
                        )

        out = [v.to_dict() for v in violations]
        return {
            "violations": out,
            "violation_count": len(out),
            "parse_error_count": int(parse_error_count),
        }

    def _validate_import_target(
        self,
        *,
        violations: list[ImportViolation],
        module_name: str,
        lineno: int,
        imported_mod: str,
        current_level: int | None,
        internal_packages: set[str],
    ) -> None:
        # Deep level_N.<submod>... is forbidden in general-stack logic (barrel-only).
        if has_deep_level_path(imported_mod):
            violations.append(
                ImportViolation(
                    file=module_name,
                    line=lineno,
                    kind="DEEP_LEVEL_PATH",
                    module=imported_mod,
                    name=None,
                    message="Deep general-stack imports must use the level_N barrel surface.",
                    suggested=None,
                )
            )

        # Wrong-level / upward checks only apply when file is under level_N/.
        if current_level is not None:
            cls = classify_general_import_from(imported_mod, current_level)
            if cls is not None:
                kind, _ = cls
                violations.append(
                    ImportViolation(
                        file=module_name,
                        line=lineno,
                        kind=kind,
                        module=imported_mod,
                        name=None,
                        message=f"General-stack import violation: {kind}.",
                        suggested=None,
                    )
                )

        # Internal module existence check (filesystem).
        if is_internal_module(imported_mod, internal_packages):
            if not module_exists(imported_mod, self.root):
                violations.append(
                    ImportViolation(
                        file=module_name,
                        line=lineno,
                        kind="INTERNAL_MODULE_NOT_FOUND",
                        module=imported_mod,
                        name=None,
                        message="Internal import target does not resolve to a module on disk.",
                        suggested=None,
                    )
                )

