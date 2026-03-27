"""Atomic models for devtools import-rule scanning."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Violation:
    kind: str
    line: int
    detail: str


@dataclass
class FileReport:
    path: Path
    parse_error: str | None = None
    violations: list[Violation] = field(default_factory=list)


__all__ = ["Violation", "FileReport"]
