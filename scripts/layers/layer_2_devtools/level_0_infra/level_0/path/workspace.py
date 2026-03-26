"""Atomic workspace path resolution helpers for devtools."""

from __future__ import annotations

from pathlib import Path


def resolve_workspace_root(start: Path, explicit_root: Path | None = None) -> Path:
    """Resolve workspace root using explicit override or deterministic discovery."""
    if explicit_root is not None:
        return explicit_root.resolve()
    return find_workspace_root(start.resolve())


def find_workspace_root(start: Path) -> Path:
    """Walk parents for a directory containing .cursor/audit-results."""
    for parent in [start, *start.parents]:
        if (parent / ".cursor" / "audit-results").is_dir():
            return parent
    raise SystemExit(
        "Could not find workspace root (missing .cursor/audit-results). "
        "Run from the Kaggle/code workspace or pass --output explicitly."
    )


__all__ = ["find_workspace_root", "resolve_workspace_root"]
