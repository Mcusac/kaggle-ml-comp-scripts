"""Remove __pycache__ trees and optional loose .pyc files (stdlib + pathlib only)."""

from dataclasses import dataclass
import os
from pathlib import Path
import shutil
import stat

SKIP_DIRS = frozenset({".git"})


def handle_rmtree_readonly(func, path: str, exc_info) -> None:
    """Clear read-only and retry so rmtree succeeds on Windows."""
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWRITE)
        func(path)
    else:
        raise exc_info[1]


def count_pyc_files_under(path: Path) -> int:
    """Count .pyc files under path (recursive)."""
    n = 0
    try:
        for item in path.rglob("*"):
            if item.is_file() and item.suffix == ".pyc":
                n += 1
    except OSError:
        pass
    return n


@dataclass
class CleanResult:
    """Result of a pycache clean run (counts for dry_run or execute)."""

    dirs_removed: int
    files_removed: int


def clean_pycache(
    root: Path,
    *,
    dry_run: bool = False,
    remove_pyc_files: bool = False,
) -> CleanResult:
    """
    Find and remove __pycache__ directories under root, and optionally loose .pyc files.

    Does not recurse into SKIP_DIRS (e.g. .git).
    """
    root = root.resolve()
    if not root.is_dir():
        return CleanResult(dirs_removed=0, files_removed=0)

    dirs_removed = 0
    files_removed = 0

    pycache_dirs: list[Path] = []
    pyc_files: list[Path] = []

    def walk(path: Path) -> None:
        try:
            for item in path.iterdir():
                if item.name in SKIP_DIRS:
                    continue
                if item.is_dir():
                    if item.name == "__pycache__":
                        pycache_dirs.append(item)
                    else:
                        walk(item)
                elif remove_pyc_files and item.suffix == ".pyc":
                    pyc_files.append(item)
        except OSError:
            pass

    walk(root)

    for d in pycache_dirs:
        files_removed += count_pyc_files_under(d)
        if dry_run:
            dirs_removed += 1
        else:
            shutil.rmtree(d, onerror=handle_rmtree_readonly)
            dirs_removed += 1

    for f in pyc_files:
        if dry_run:
            files_removed += 1
        else:
            try:
                f.unlink()
                files_removed += 1
            except OSError:
                pass

    return CleanResult(dirs_removed=dirs_removed, files_removed=files_removed)