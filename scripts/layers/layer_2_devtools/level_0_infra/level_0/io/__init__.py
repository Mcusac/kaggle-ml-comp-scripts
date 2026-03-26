"""I/O primitives (non-destructive)."""

from .json_fs import (
    latest_path_by_glob_mtime,
    read_json_object,
)
from .text_file import count_lines, read_file_safe

__all__ = [
    "count_lines",
    "latest_path_by_glob_mtime",
    "read_file_safe",
    "read_json_object",
]
