from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class EditOperation:
    """A single, safe text replacement anchored to a line number."""

    path: Path
    line: int
    kind: str
    old_line: str
    new_line: str


@dataclass(frozen=True)
class FileEditResult:
    path: Path
    edits_applied: int


@dataclass(frozen=True)
class FixRunSummary:
    files_considered: int
    files_changed: int
    edits_applied: int

