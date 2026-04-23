"""Atomic models for devtools import-rule scanning."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Violation:
    kind: str
    line: int
    detail: str
    file_level: int | None = None
    imported_level: int | None = None
    suggested_min_level: int | None = None


@dataclass
class FileReport:
    path: Path
    parse_error: str | None = None
    violations: list[Violation] = field(default_factory=list)