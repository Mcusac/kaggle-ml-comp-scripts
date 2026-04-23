"""Static barrel (``__init__.py``) public names for import-surface enforcement."""

from __future__ import annotations

import ast
from pathlib import Path

from layers.layer_2_devtools.level_0_infra.level_0.parse.ast.ast_utils import parse_file


def load_static_barrel_names(level_j_dir: Path) -> set[str]:
    """Load public names from ``level_j_dir/__init__.py`` (static ``__all__`` + relative re-exports).

    Heuristic only: dynamic ``__all__`` is not modeled (same disclaimer as contest scans).
    """
    init_py = level_j_dir / "__init__.py"
    if not init_py.is_file():
        return set()
    tree = parse_file(init_py)
    if tree is None or not isinstance(tree, ast.Module):
        return set()
    return static_all_names_from_module(tree) | reexport_names_from_init_module(tree)


def static_all_names_from_module(tree: ast.Module) -> set[str]:
    """Names from top-level ``__all__ = (...,)`` string entries."""
    names: set[str] = set()
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "__all__":
                value = node.value
                if isinstance(value, (ast.List, ast.Tuple)):
                    for elt in value.elts:
                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                            names.add(elt.value)
    return names


def reexport_names_from_init_module(tree: ast.Module) -> set[str]:
    """Names introduced by ``from .x import y`` at package init (as public re-exports)."""
    names: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.level == 1 and node.module:
            for alias in node.names:
                if alias.name != "*":
                    names.add(alias.name if alias.asname is None else alias.asname)
    return names
