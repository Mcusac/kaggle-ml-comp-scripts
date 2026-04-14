"""Atomic AST parsing utilities for devtools analyzers."""

import ast
from pathlib import Path


def parse_file(file_path: Path) -> ast.AST | None:
    """Parse a Python file into an AST, returning None on parse/read failure."""
    try:
        return ast.parse(file_path.read_text(encoding="utf-8"), filename=str(file_path))
    except (SyntaxError, OSError):
        return None


def resolve_relative_import(
    level: int, current_pkg: str, node_module: str | None
) -> str | None:
    """Resolve relative import components to an absolute module path."""
    if level < 1:
        return node_module
    pkg_parts = current_pkg.split(".") if current_pkg else []
    up_index = max(0, len(pkg_parts) - (level - 1))
    base = ".".join(pkg_parts[:up_index])
    if node_module:
        return f"{base}.{node_module}" if base else node_module
    return base or None


def get_imports_from_ast(tree: ast.AST, current_pkg: str = "") -> dict[str, set[str]]:
    """Extract import statements from AST as module -> imported names."""
    imports: dict[str, set[str]] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.setdefault(alias.name, set())
        elif isinstance(node, ast.ImportFrom):
            level = getattr(node, "level", 0)
            resolved = (
                resolve_relative_import(level, current_pkg, node.module)
                if level >= 1
                else node.module
            )
            if not resolved:
                continue
            imports.setdefault(resolved, set())
            for alias in node.names:
                imports[resolved].add(alias.asname or alias.name)
    return imports


def get_imports_from_file(
    file_path: Path, current_pkg: str = ""
) -> dict[str, set[str]]:
    """Extract import statements from a Python file."""
    tree = parse_file(file_path)
    if tree is None:
        return {}
    return get_imports_from_ast(tree, current_pkg)


def count_function_nodes(tree: ast.AST) -> int:
    """Count function and async function definitions in AST."""
    return sum(
        1
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    )


def count_class_nodes(tree: ast.AST) -> int:
    """Count class definitions in AST."""
    return sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))


def get_function_complexity(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """Compute simplified McCabe-style complexity for a function node."""
    complexity = 1
    for child in ast.walk(node):
        if isinstance(
            child, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.With, ast.Assert)
        ):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
    return complexity


def get_all_functions(
    tree: ast.AST,
) -> list[tuple[str, ast.FunctionDef | ast.AsyncFunctionDef]]:
    """Return all function definitions as name/node pairs."""
    return [
        (node.name, node)
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]


def get_all_classes(tree: ast.AST) -> list[tuple[str, ast.ClassDef]]:
    """Return all class definitions as name/node pairs."""
    return [
        (node.name, node) for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
    ]


def count_lines_in_node(node: ast.AST) -> int:
    """Return line span for an AST node, or zero when unavailable."""
    if not hasattr(node, "lineno") or not hasattr(node, "end_lineno"):
        return 0
    return (node.end_lineno or node.lineno) - node.lineno + 1


def get_relative_imports_from_ast(
    tree: ast.AST, current_pkg: str = ""
) -> list[dict[str, int | str | None]]:
    """Extract metadata for relative ImportFrom statements."""
    relative_imports: list[dict[str, int | str | None]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            level = getattr(node, "level", 0)
            if level >= 1:
                module = node.module
                resolved = resolve_relative_import(level, current_pkg, module)
                dots = "." * level
                original = f"from {dots}{module} import ..." if module else f"from {dots} import ..."
                relative_imports.append(
                    {
                        "level": level,
                        "module": module,
                        "resolved_name": resolved,
                        "line_number": getattr(node, "lineno", 0),
                        "original_syntax": original,
                    }
                )
    return relative_imports