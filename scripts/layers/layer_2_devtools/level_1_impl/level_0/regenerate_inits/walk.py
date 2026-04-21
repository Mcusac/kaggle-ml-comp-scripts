"""Filesystem walking utilities for deterministic `__init__.py` generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


SKIP_DIRS = frozenset({"__pycache__", ".git", ".venv", "venv", "node_modules"})


@dataclass(frozen=True)
class PackageContents:
    package_dir: Path
    subpackages: list[str]
    modules: list[str]


def _is_skipped_dir(path: Path, include_tests: bool) -> bool:
    name = path.name
    if name in SKIP_DIRS:
        return True
    if name.startswith(".") or name.startswith("_"):
        return True
    if not include_tests and name == "tests":
        return True
    return False


def _eligible_module_file(path: Path) -> bool:
    if path.suffix != ".py":
        return False
    if path.name == "__init__.py":
        return False
    if path.name.startswith("test_"):
        return False
    return True


def is_package_dir(path: Path, include_tests: bool) -> bool:
    if not path.is_dir():
        return False
    if _is_skipped_dir(path, include_tests=include_tests):
        return False
    init_file = path / "__init__.py"
    if init_file.exists():
        return True
    # Treat a directory with any eligible *.py files or eligible subdirs as a package candidate.
    for item in path.iterdir():
        if item.is_file() and _eligible_module_file(item):
            return True
        if item.is_dir() and not _is_skipped_dir(item, include_tests=include_tests):
            if (item / "__init__.py").exists():
                return True
    return False


def collect_package_dirs(root: Path, include_tests: bool) -> list[Path]:
    """
    Collect all package-like directories under `root`, including `root` itself if eligible.

    Returned order is not guaranteed; callers should sort bottom-up (deepest first).
    """
    root = root.resolve()
    out: list[Path] = []

    if is_package_dir(root, include_tests=include_tests):
        out.append(root)

    for path in root.rglob("*"):
        if not path.is_dir():
            continue
        if not is_package_dir(path, include_tests=include_tests):
            continue
        out.append(path)

    # Deterministic: unique + sorted path string
    uniq = sorted({p.resolve() for p in out}, key=lambda p: str(p))
    return list(uniq)


def bottom_up_package_dirs(root: Path, include_tests: bool) -> list[Path]:
    pkgs = collect_package_dirs(root, include_tests=include_tests)
    return sorted(pkgs, key=lambda p: (len(p.parts), str(p)), reverse=True)


def read_package_contents(package_dir: Path, include_tests: bool) -> PackageContents:
    subpackages: list[str] = []
    modules: list[str] = []

    for item in sorted(package_dir.iterdir(), key=lambda p: p.name):
        if item.is_dir():
            if _is_skipped_dir(item, include_tests=include_tests):
                continue
            if (item / "__init__.py").exists():
                subpackages.append(item.name)
            continue

        if item.is_file() and _eligible_module_file(item):
            modules.append(item.stem)

    return PackageContents(
        package_dir=package_dir,
        subpackages=subpackages,
        modules=modules,
    )

