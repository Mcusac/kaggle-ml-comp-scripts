"""Small text file read helpers (UTF-8)."""

from pathlib import Path


def count_lines(path: Path) -> int:
    try:
        return sum(1 for _ in path.read_text(encoding="utf-8").splitlines())
    except OSError:
        return 0


def read_file_safe(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return None


__all__ = ["count_lines", "read_file_safe"]
