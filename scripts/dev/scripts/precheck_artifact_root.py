"""Resolve audit artifact root without importing ``layers`` (CLI fallback only)."""

from __future__ import annotations

from pathlib import Path


def is_kaggle_ml_comp_scripts_package_root(path: Path) -> bool:
    p = path.resolve()
    return (
        (p / "scripts").is_dir()
        and (p / "scripts" / "layers").is_dir()
        and (p / ".cursor").is_dir()
    )


def resolve_audit_artifact_root(start: Path) -> Path:
    anchor = start.resolve()
    if anchor.is_file():
        anchor = anchor.parent
    first_hit: Path | None = None
    for parent in (anchor, *anchor.parents):
        audit_results = parent / ".cursor" / "audit-results"
        if not audit_results.is_dir():
            continue
        if first_hit is None:
            first_hit = parent
        if is_kaggle_ml_comp_scripts_package_root(parent):
            return parent
    if first_hit is not None:
        return first_hit
    for parent in (anchor, *anchor.parents):
        if (parent / ".cursor").is_dir():
            return parent
    return anchor


__all__ = ["is_kaggle_ml_comp_scripts_package_root", "resolve_audit_artifact_root"]
