"""Static checks for safe ``__all__`` aggregation (list/tuple concat hazards)."""

from __future__ import annotations

import ast
from pathlib import Path


def find_scripts_root(start: Path | None = None) -> Path:
    here = (start or Path(__file__)).resolve()
    for parent in here.parents:
        if (parent / "layers").is_dir():
            return parent
    raise AssertionError("Could not locate scripts root from path")


def iter_py_files(root: Path) -> list[Path]:
    return sorted(root.glob("**/*.py"))


def _is_list_wrapped_all(node: ast.AST) -> bool:
    return (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "list"
        and len(node.args) == 1
        and isinstance(node.args[0], ast.Attribute)
        and node.args[0].attr == "__all__"
    )


def _flatten_add_chain(node: ast.AST) -> list[ast.AST]:
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return _flatten_add_chain(node.left) + _flatten_add_chain(node.right)
    return [node]


def collect_init_all_concat_violations(scripts_root: Path) -> list[str]:
    """Return human-readable violation lines for unsafe ``__all__ +=`` patterns."""
    violations: list[str] = []

    for path in iter_py_files(scripts_root):
        if path.name != "__init__.py":
            continue

        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:
            if not isinstance(node, ast.Assign):
                continue
            if len(node.targets) != 1:
                continue
            target = node.targets[0]
            if not isinstance(target, ast.Name) or target.id != "__all__":
                continue

            if not isinstance(node.value, ast.BinOp):
                continue

            parts = _flatten_add_chain(node.value)
            for part in parts:
                if isinstance(part, ast.Tuple):
                    violations.append(f"{path}: tuple literal in __all__ concat chain")
                    continue

                if isinstance(part, ast.Attribute) and part.attr == "__all__":
                    violations.append(f"{path}: raw child __all__ used without list(...)")
                    continue

                if (
                    isinstance(part, ast.Call)
                    and isinstance(part.func, ast.Name)
                    and part.func.id == "list"
                ):
                    if not _is_list_wrapped_all(part):
                        violations.append(
                            f"{path}: list(...) in __all__ concat must wrap child __all__"
                        )
                    continue

                if isinstance(part, ast.List):
                    continue

                violations.append(
                    f"{path}: unsupported __all__ concat part type {type(part).__name__}"
                )

    return violations
