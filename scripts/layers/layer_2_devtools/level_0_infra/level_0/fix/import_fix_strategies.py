from __future__ import annotations

import ast
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from layers.layer_2_devtools.level_0_infra.level_0.constants.import_patterns import (
    DEEP_LEVEL_RE,
    LEVEL_DIR_RE,
)
from layers.layer_2_devtools.level_0_infra.level_0.fix.import_fix_models import EditOperation
from layers.layer_2_devtools.level_0_infra.level_0.parse.ast.ast_utils import (
    parse_file,
    resolve_relative_import,
)
from layers.layer_2_devtools.level_0_infra.level_0.path.python_modules import (
    current_package,
    discover_packages,
    is_internal_module,
    module_exists,
)


_LAYER0_CORE_PREFIX = "layers.layer_0_core."


@dataclass(frozen=True)
class FixOptions:
    include_tests: bool = False
    rewrite_relative_in_logic: str = "off"  # "off" | "absolute"


def iter_python_files(root: Path, *, include_tests: bool) -> list[Path]:
    files: list[Path] = []
    for p in sorted(root.rglob("*.py")):
        if not include_tests and p.name.startswith("test_"):
            continue
        files.append(p)
    return files


def build_edit_operations_for_tree(
    *,
    root: Path,
    scripts_root: Path,
    opts: FixOptions,
) -> tuple[list[EditOperation], list[str]]:
    # General-stack `level_N` packages live under layer_0_core. These utilities
    # operate on filesystem roots, not runtime sys.path state.
    layer_0_core = (scripts_root / "layers" / "layer_0_core").resolve()
    general_root = layer_0_core if layer_0_core.is_dir() else scripts_root.resolve()
    internal_packages = discover_packages(general_root)
    errors: list[str] = []
    ops: list[EditOperation] = []

    exported_cache: dict[Path, set[str]] = {}

    for path in iter_python_files(root, include_tests=opts.include_tests):
        tree = parse_file(path)
        if tree is None:
            continue

        # For relative import resolution, choose a package root that contains the file.
        pkg_root = general_root if _is_within(path, general_root) else scripts_root.resolve()
        pkg = current_package(path, pkg_root)
        is_logic = path.name != "__init__.py"

        if _file_uses_explicit_layer0_core(tree):
            ops.extend(_ops_fix_layer0_core_mixed_style(path, tree))

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                lineno = int(getattr(node, "lineno", 0) or 0)
                end_lineno = int(getattr(node, "end_lineno", lineno) or lineno)
                if lineno <= 0:
                    continue
                if end_lineno != lineno:
                    continue  # multi-line imports are not rewritten (safe-only)

                # (A) Relative imports in logic: optional absolute rewrite.
                if is_logic and getattr(node, "level", 0) and getattr(node, "level", 0) > 0:
                    if opts.rewrite_relative_in_logic != "absolute":
                        continue
                    resolved = resolve_relative_import(int(node.level), pkg, node.module)
                    if not resolved:
                        continue
                    if DEEP_LEVEL_RE.match(resolved):
                        continue
                    if not is_internal_module(resolved, internal_packages):
                        continue
                    if not module_exists(resolved, pkg_root):
                        continue
                    old_line = _get_source_line(path, lineno)
                    if old_line is None:
                        continue
                    names = _extract_importfrom_names(node)
                    if not names:
                        continue
                    new_line = _render_from_import(old_line, resolved, names)
                    if new_line is None or new_line == old_line:
                        continue
                    ops.append(
                        EditOperation(
                            path=path,
                            line=lineno,
                            kind="RELATIVE_IN_LOGIC_ABSOLUTE",
                            old_line=old_line,
                            new_line=new_line,
                        )
                    )
                    continue

                # (B) Deep level imports: rewrite to barrel when provable.
                if getattr(node, "level", 0):
                    continue  # skip relative here; handled above
                if not isinstance(node.module, str) or not node.module:
                    continue
                if not DEEP_LEVEL_RE.match(node.module):
                    continue

                m = DEEP_LEVEL_RE.match(node.module)
                if not m:
                    continue
                barrel = f"level_{int(m.group(1))}"
                init_py = general_root / barrel / "__init__.py"
                if not init_py.is_file():
                    continue
                if init_py not in exported_cache:
                    exported_cache[init_py] = _exported_names_from_init(init_py)
                exported = exported_cache[init_py]

                imported_names = _extract_importfrom_names(node)
                if not imported_names:
                    continue
                # All imported names must be exported for an automatic rewrite.
                if any(n not in exported for n in imported_names):
                    continue

                old_line = _get_source_line(path, lineno)
                if old_line is None:
                    continue

                new_line = _render_from_import(old_line, barrel, imported_names)
                if new_line is None or new_line == old_line:
                    continue
                ops.append(
                    EditOperation(
                        path=path,
                        line=lineno,
                        kind="DEEP_LEVEL_PATH_CANONICAL",
                        old_line=old_line,
                        new_line=new_line,
                    )
                )
            elif isinstance(node, ast.Import):
                # Mixed style import rewrite: `import level_N` -> `import layers.layer_0_core.level_N as level_N`
                if not _file_uses_explicit_layer0_core(tree):
                    continue
                lineno = int(getattr(node, "lineno", 0) or 0)
                end_lineno = int(getattr(node, "end_lineno", lineno) or lineno)
                if lineno <= 0 or end_lineno != lineno:
                    continue
                old_line = _get_source_line(path, lineno)
                if old_line is None:
                    continue
                repl = _rewrite_import_level_line(old_line)
                if repl and repl != old_line:
                    ops.append(
                        EditOperation(
                            path=path,
                            line=lineno,
                            kind="LAYER0_CORE_MIXED_IMPORT_STYLE",
                            old_line=old_line,
                            new_line=repl,
                        )
                    )

    return ops, errors


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _file_uses_explicit_layer0_core(tree: ast.AST) -> bool:
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and str(node.module).startswith(
            _LAYER0_CORE_PREFIX
        ):
            return True
    return False


_FROM_LEVEL_LINE_RE = re.compile(
    r"^(?P<indent>[ \t]*)from[ \t]+level_(?P<n>\d+)[ \t]+import[ \t]+"
)
_IMPORT_LEVEL_LINE_RE = re.compile(r"^(?P<indent>[ \t]*)import[ \t]+level_(?P<n>\d+)\b")


def _ops_fix_layer0_core_mixed_style(path: Path, tree: ast.AST) -> list[EditOperation]:
    ops: list[EditOperation] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom):
            continue
        if getattr(node, "level", 0):
            continue
        module = node.module
        if not isinstance(module, str) or not LEVEL_DIR_RE.fullmatch(module):
            continue
        lineno = int(getattr(node, "lineno", 0) or 0)
        end_lineno = int(getattr(node, "end_lineno", lineno) or lineno)
        if lineno <= 0 or end_lineno != lineno:
            continue
        old_line = _get_source_line(path, lineno)
        if old_line is None:
            continue
        rewritten = _rewrite_from_level_line(old_line)
        if rewritten and rewritten != old_line:
            ops.append(
                EditOperation(
                    path=path,
                    line=lineno,
                    kind="LAYER0_CORE_MIXED_IMPORT_STYLE",
                    old_line=old_line,
                    new_line=rewritten,
                )
            )
    return ops


def _rewrite_from_level_line(line: str) -> str | None:
    m = _FROM_LEVEL_LINE_RE.match(line)
    if not m:
        return None
    indent = m.group("indent")
    n = m.group("n")
    rest = line[m.end() :]
    return f"{indent}from layers.layer_0_core.level_{n} import {rest}"


def _rewrite_import_level_line(line: str) -> str | None:
    m = _IMPORT_LEVEL_LINE_RE.match(line)
    if not m:
        return None
    indent = m.group("indent")
    n = m.group("n")
    rest = line[m.end() :]
    # Preserve trailing comment / whitespace.
    return f"{indent}import layers.layer_0_core.level_{n} as level_{n}{rest}"


def _get_source_line(path: Path, lineno: int) -> str | None:
    try:
        text = path.read_bytes().decode("utf-8")
        lines = text.splitlines(keepends=True)
    except OSError:
        return None
    if lineno <= 0 or lineno > len(lines):
        return None
    return lines[lineno - 1]


def _extract_importfrom_names(node: ast.ImportFrom) -> list[str]:
    out: list[str] = []
    for alias in getattr(node, "names", []):
        name = getattr(alias, "name", None)
        if isinstance(name, str) and name and name != "*":
            out.append(name)
    return out


def _render_from_import(original_line: str, module: str, names: Iterable[str]) -> str | None:
    stripped = original_line.lstrip()
    indent = original_line[: len(original_line) - len(stripped)]
    if not stripped.startswith("from "):
        return None
    nl = "\r\n" if original_line.endswith("\r\n") else "\n" if original_line.endswith("\n") else ""
    names_part = ", ".join(names)
    return f"{indent}from {module} import {names_part}{nl}"


def _exported_names_from_init(init_py: Path) -> set[str]:
    """Conservative export discovery for __init__.py (rewrite-only tooling).

    Supports:
    - __all__ assignments with a tuple/list of string literals
    - relative `from .mod import X` re-exports (collect alias/asname)
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
                for alias in getattr(node, "names", []):
                    name = getattr(alias, "name", None)
                    asname = getattr(alias, "asname", None)
                    if isinstance(name, str) and name and name != "*":
                        exports.add(str(asname or name))
    return exports

