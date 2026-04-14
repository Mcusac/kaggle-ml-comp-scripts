"""JSON file reads and directory glob selection."""

import json
from pathlib import Path
from typing import Any


def read_json_object(path: Path) -> dict[str, Any]:
    """Read UTF-8 JSON object from path."""
    return json.loads(path.read_text(encoding="utf-8"))


def latest_path_by_glob_mtime(directory: Path, pattern: str) -> Path:
    """Return newest file matching glob under directory by mtime."""
    files = sorted(
        directory.glob(pattern),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not files:
        raise FileNotFoundError(f"No files matching {pattern!r} under {directory}")
    return files[0]