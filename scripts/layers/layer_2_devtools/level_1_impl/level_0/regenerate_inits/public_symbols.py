"""Extract public top-level symbols from Python modules."""

from __future__ import annotations

import ast
from pathlib import Path


def public_symbols_from_module(source: str) -> list[str]:
    """
    Return public top-level symbols for a leaf module.

    Rules (v1):
    - include: top-level `class`, `def`, `async def`
    - include: simple module-level assignments to a single `Name` target
    - exclude: anything starting with `_`
    - exclude: imported names (this is a pure AST-definition surface)
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    out: set[str] = set()

    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            name = node.name
            if not name.startswith("_"):
                out.add(name)
            continue

        if isinstance(node, ast.Assign):
            if len(node.targets) != 1:
                continue
            target = node.targets[0]
            if isinstance(target, ast.Name) and not target.id.startswith("_"):
                out.add(target.id)
            continue

        if isinstance(node, ast.AnnAssign):
            target = node.target
            if isinstance(target, ast.Name) and not target.id.startswith("_"):
                out.add(target.id)
            continue

    return sorted(out)


def public_symbols_from_file(path: Path) -> list[str]:
    try:
        src = path.read_text(encoding="utf-8")
    except OSError:
        return []
    return public_symbols_from_module(src)

