"""Module discovery and resolution utilities."""

import re
from pathlib import Path

SKIP_DIRS = frozenset({"__pycache__", ".git", ".venv", "venv", "node_modules"})
SKIP_FILES_RE = re.compile(r"^test_.*\.py$")


def file_to_module(file_path: Path, root: Path) -> str | None:
    """Convert file path to module name relative to root."""
    try:
        rel = file_path.resolve().relative_to(root.resolve())
    except ValueError:
        return None

    parts = list(rel.parts)

    if parts and parts[-1] == "__init__.py":
        parts = parts[:-1]
        return ".".join(parts) if parts else None

    if parts and parts[-1].endswith(".py"):
        parts[-1] = parts[-1][:-3]

    return ".".join(parts) if parts else None


def current_package(file_path: Path, root: Path) -> str:
    """Package name for a file (parent package for non-__init__ modules)."""
    mod = file_to_module(file_path, root)
    if not mod:
        return ""

    if file_path.name == "__init__.py":
        return mod

    parts = mod.split(".")
    return ".".join(parts[:-1]) if len(parts) > 1 else ""


def collect_python_files(root: Path, include_tests: bool = False) -> list[Path]:
    """Recursively collect Python files from directory."""
    files: list[Path] = []

    for path in root.rglob("*.py"):
        if SKIP_DIRS & set(path.parts):
            continue

        if not include_tests and SKIP_FILES_RE.match(path.name):
            continue

        files.append(path)

    return sorted(files, key=str)


def discover_packages(root: Path) -> set[str]:
    """Discover top-level package-like directory names under root."""
    packages: set[str] = set()

    for item in root.iterdir():
        if not item.is_dir():
            continue

        if item.name.startswith("_") or item.name.startswith("."):
            continue

        if item.name in SKIP_DIRS:
            continue

        init_file = item / "__init__.py"
        has_py_files = any(f.is_file() and f.suffix == ".py" for f in item.iterdir())

        if init_file.exists() or has_py_files:
            packages.add(item.name)

    return packages


def discover_modules_in_package(package_name: str, package_root: Path) -> list[str]:
    """Recursively list module dotted paths under a package root."""
    modules: list[str] = []

    def walk_package(path: Path, current_module: str) -> None:
        for item in sorted(path.iterdir()):
            if (
                item.name.startswith("test_")
                or item.name == "__pycache__"
                or item.name.startswith(".")
            ):
                continue

            if item.is_file() and item.suffix == ".py":
                if item.stem != "__init__":
                    modules.append(f"{current_module}.{item.stem}")

            elif item.is_dir() and not item.name.startswith("_") and not item.name.startswith("."):
                init_file = item / "__init__.py"
                if init_file.exists():
                    new_module = f"{current_module}.{item.name}"
                    modules.append(new_module)
                    walk_package(item, new_module)

    walk_package(package_root, package_name)
    return sorted(modules)


def is_internal_module(module: str, internal_packages: set[str]) -> bool:
    return module.split(".")[0] in internal_packages


def is_third_party_module(module: str, internal_packages: set[str]) -> bool:
    return not is_internal_module(module, internal_packages)


def module_exists(module_name: str, root: Path) -> bool:
    """True if module resolves to a .py file or package with __init__.py under root."""
    if not module_name:
        return False

    parts = module_name.split(".")
    module_path = root / Path(*parts)

    py_file = module_path.with_suffix(".py")
    if py_file.exists() and py_file.is_file():
        return True

    init_file = module_path / "__init__.py"
    if init_file.exists() and init_file.is_file():
        return True

    return False


__all__ = [
    "SKIP_DIRS",
    "SKIP_FILES_RE",
    "collect_python_files",
    "current_package",
    "discover_modules_in_package",
    "discover_packages",
    "file_to_module",
    "is_internal_module",
    "is_third_party_module",
    "module_exists",
]
