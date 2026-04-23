"""Extract public top-level symbols from Python modules (devtools infra)."""

import ast

DEFAULT_EXCLUDED_SYMBOLS = frozenset({"main"})


def is_public_symbol(name: str, *, excluded: set[str]) -> bool:
    if not name:
        return False
    if name in excluded:
        return False
    if name.startswith("_"):
        return False
    if name.startswith("__") and name.endswith("__"):
        return False
    return True


def public_symbols_from_module(source: str, *, exclude: set[str] | None = None) -> list[str]:
    """
    Return public top-level symbols for a leaf module.

    Rules (v1):
    - include: top-level `class`, `def`, `async def`
    - include: simple module-level assignments to a single `Name` target
    - exclude: anything starting with `_` (including dunders)
    - exclude: names in `exclude` (default: `DEFAULT_EXCLUDED_SYMBOLS`)
    - exclude: imported names (this is a pure AST-definition surface)
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    excluded = set(DEFAULT_EXCLUDED_SYMBOLS) if exclude is None else set(exclude)

    out: set[str] = set()

    for node in tree.body:
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            name = node.name
            if is_public_symbol(name, excluded=excluded):
                out.add(name)
            continue

        if isinstance(node, ast.Assign):
            if len(node.targets) != 1:
                continue
            target = node.targets[0]
            if isinstance(target, ast.Name) and is_public_symbol(target.id, excluded=excluded):
                out.add(target.id)
            continue

        if isinstance(node, ast.AnnAssign):
            target = node.target
            if isinstance(target, ast.Name) and is_public_symbol(target.id, excluded=excluded):
                out.add(target.id)
            continue

    return sorted(out)

