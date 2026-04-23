from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from layers.layer_2_devtools.level_0_infra.level_0.fix.import_fix_models import EditOperation
from layers.layer_2_devtools.level_0_infra.level_0.parse.ast.ast_utils import parse_file
from layers.layer_2_devtools.level_0_infra.level_0.path.python_modules import collect_python_files


@dataclass(frozen=True)
class MoveImportRewrite:
    old_module: str
    new_module: str

    @property
    def old_parent(self) -> str:
        parts = self.old_module.split(".")
        return ".".join(parts[:-1]) if len(parts) > 1 else ""

    @property
    def new_parent(self) -> str:
        parts = self.new_module.split(".")
        return ".".join(parts[:-1]) if len(parts) > 1 else ""

    @property
    def old_leaf(self) -> str:
        return self.old_module.split(".")[-1] if self.old_module else ""

    @property
    def new_leaf(self) -> str:
        return self.new_module.split(".")[-1] if self.new_module else ""


def build_move_import_rewrite_ops(
    *,
    root: Path,
    rewrite: MoveImportRewrite,
    include_tests: bool = False,
) -> tuple[list[EditOperation], list[str]]:
    """Build drift-safe edit operations to rewrite imports referencing a moved module.

    Notes:
    - Uses line-based edits (safe drift-checked replacements).
    - Multi-line imports are supported by rewriting only the first line.
    - Only rewrites import statements whose semantic target matches the moved module.
    """
    root = root.resolve()
    if not root.is_dir():
        return [], [f"root is not a directory: {root.as_posix()}"]

    if not rewrite.old_module or not rewrite.new_module:
        return [], ["old_module and new_module must be non-empty."]

    ops: list[EditOperation] = []
    warnings: list[str] = []

    for path in collect_python_files(root, include_tests=include_tests):
        file_ops, file_warn = _build_ops_for_file(path=path, rewrite=rewrite)
        ops.extend(file_ops)
        warnings.extend(file_warn)

    return ops, warnings


def _build_ops_for_file(
    *,
    path: Path,
    rewrite: MoveImportRewrite,
) -> tuple[list[EditOperation], list[str]]:
    try:
        raw = path.read_bytes().decode("utf-8")
    except OSError as exc:
        return [], [str(exc)]
    # Preserve original newlines so EditOperation drift-checks match exactly.
    lines = raw.splitlines(keepends=True)

    tree = parse_file(path)
    if tree is None:
        return [], []

    out: list[EditOperation] = []
    warnings: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            op = _maybe_rewrite_import_node(path=path, lines=lines, node=node, rewrite=rewrite)
            if op is not None:
                out.append(op)
        elif isinstance(node, ast.ImportFrom):
            op = _maybe_rewrite_importfrom_node(
                path=path, lines=lines, node=node, rewrite=rewrite
            )
            if op is not None:
                out.append(op)

    return out, warnings


def _maybe_rewrite_import_node(
    *,
    path: Path,
    lines: list[str],
    node: ast.Import,
    rewrite: MoveImportRewrite,
) -> EditOperation | None:
    lineno = int(getattr(node, "lineno", 0) or 0)
    end_lineno = int(getattr(node, "end_lineno", lineno) or lineno)
    if lineno <= 0 or end_lineno < lineno:
        return None

    changed = False
    parts: list[str] = []
    for a in getattr(node, "names", []):
        name = getattr(a, "name", None)
        if not isinstance(name, str) or not name:
            continue
        asname = getattr(a, "asname", None)
        new_name = rewrite.new_module if name == rewrite.old_module else name
        if new_name != name:
            changed = True
        if asname:
            parts.append(f"{new_name} as {asname}")
        else:
            parts.append(new_name)

    if not changed or not parts:
        return None

    old_line = lines[lineno - 1]
    indent = _leading_whitespace(old_line)
    nl = "\n" if old_line.endswith("\n") else ""
    new_line = f"{indent}import {', '.join(parts)}{nl}"
    if new_line == old_line:
        return None
    return EditOperation(
        path=path,
        line=lineno,
        kind="MOVE_IMPORT_REWRITE",
        old_line=old_line,
        new_line=new_line,
    )


def _maybe_rewrite_importfrom_node(
    *,
    path: Path,
    lines: list[str],
    node: ast.ImportFrom,
    rewrite: MoveImportRewrite,
) -> EditOperation | None:
    if int(getattr(node, "level", 0) or 0) != 0:
        # Safe Move Planner should not guess relative imports here.
        return None

    module = getattr(node, "module", None)
    if not isinstance(module, str) or not module:
        return None

    lineno = int(getattr(node, "lineno", 0) or 0)
    end_lineno = int(getattr(node, "end_lineno", lineno) or lineno)
    if lineno <= 0 or end_lineno < lineno:
        return None

    new_module: str | None = None
    if module == rewrite.old_module:
        new_module = rewrite.new_module
    elif module == rewrite.old_parent and rewrite.old_leaf and rewrite.new_leaf:
        # from old_parent import old_leaf  -> from new_parent import new_leaf
        for a in getattr(node, "names", []):
            name = getattr(a, "name", None)
            if name == rewrite.old_leaf:
                new_module = rewrite.new_parent
                break

    if new_module is None:
        return None

    old_line = lines[lineno - 1]
    new_line = _rewrite_from_import_line(
        old_line=old_line,
        old_module=module,
        new_module=new_module,
        old_leaf=rewrite.old_leaf,
        new_leaf=rewrite.new_leaf,
    )
    if new_line is None or new_line == old_line:
        return None
    return EditOperation(
        path=path,
        line=lineno,
        kind="MOVE_IMPORTFROM_REWRITE",
        old_line=old_line,
        new_line=new_line,
    )


def _rewrite_from_import_line(
    *,
    old_line: str,
    old_module: str,
    new_module: str,
    old_leaf: str,
    new_leaf: str,
) -> str | None:
    """Rewrite only the `from <module> import` header line (drift-safe)."""
    stripped = old_line.lstrip()
    indent = old_line[: len(old_line) - len(stripped)]
    if not stripped.startswith("from "):
        return None
    if f"from {old_module} import" not in stripped:
        # drift guard: do not guess
        return None
    new_line = indent + stripped.replace(
        f"from {old_module} import", f"from {new_module} import", 1
    )

    # Optional: rename imported leaf only when trivial (single-line, no alias).
    if old_leaf and new_leaf and old_leaf != new_leaf:
        new_line = new_line.replace(f"import {old_leaf}", f"import {new_leaf}", 1)

    return new_line


def _leading_whitespace(line: str) -> str:
    i = 0
    while i < len(line) and line[i] in (" ", "\t"):
        i += 1
    return line[:i]

