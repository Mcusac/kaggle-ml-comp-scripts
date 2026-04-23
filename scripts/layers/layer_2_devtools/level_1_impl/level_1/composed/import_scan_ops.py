"""Shared import scanning utilities (AST-based, no runtime importing)."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path

from layers.layer_2_devtools.level_0_infra.level_0.parse.ast.ast_utils import resolve_relative_import


@dataclass(frozen=True)
class ScannedImport:
    import_text: str
    target_module: str


def is_under_impl_tests(path: Path) -> bool:
    parts = path.parts
    if any(
        parts[i] == "level_1_impl" and parts[i + 1] == "tests"
        for i in range(len(parts) - 1)
    ):
        return True
    return any(parts[i] == "impl" and parts[i + 1] == "tests" for i in range(len(parts) - 1))


def collect_py_files(*, roots: list[Path]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            if is_under_impl_tests(path):
                continue
            files.append(path.resolve())
    return sorted(files)


def module_name(*, scripts_root: Path, file_path: Path) -> str:
    rel = file_path.resolve().relative_to(scripts_root.resolve())
    parts = list(rel.parts)
    parts[-1] = parts[-1].removesuffix(".py")
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def build_module_map(*, scripts_root: Path, files: list[Path]) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for file_path in files:
        out[module_name(scripts_root=scripts_root, file_path=file_path)] = file_path
    return out


def extract_imports(*, file_path: Path, current_module: str) -> list[ScannedImport]:
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(file_path))
    imports: list[ScannedImport] = []
    current_pkg = current_module.rsplit(".", 1)[0] if "." in current_module else ""
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name:
                    imports.append(ScannedImport(import_text=f"import {alias.name}", target_module=alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.level and node.level > 0:
                resolved = resolve_relative_import(node.level, current_pkg, node.module)
                import_text = f"from {'.' * node.level}{node.module or ''} import ..."
            else:
                resolved = node.module
                import_text = f"from {node.module or ''} import ..."
            if resolved:
                imports.append(ScannedImport(import_text=import_text, target_module=resolved))
    return imports

