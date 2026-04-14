"""Atomic workspace path resolution helpers for devtools."""

from pathlib import Path


def resolve_workspace_root(start: Path, explicit_root: Path | None = None) -> Path:
    """Resolve workspace root using explicit override or deterministic discovery."""
    if explicit_root is not None:
        return explicit_root.resolve()
    return find_workspace_root(start.resolve())


def is_kaggle_ml_comp_scripts_package_root(path: Path) -> bool:
    """True if ``path`` looks like ``input/kaggle-ml-comp-scripts`` (has ``scripts/layers`` + ``.cursor``)."""
    p = path.resolve()
    return (
        (p / "scripts").is_dir()
        and (p / "scripts" / "layers").is_dir()
        and (p / ".cursor").is_dir()
    )


def find_workspace_root(start: Path) -> Path:
    """Walk parents for ``.cursor/audit-results``; prefer kaggle-ml-comp-scripts package root.

    When both the multi-repo workspace and ``input/kaggle-ml-comp-scripts`` expose
    ``.cursor/audit-results``, anchors under the package resolve to the package so
    planner/auditor/precheck outputs stay aligned.
    """
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
    raise SystemExit(
        "Could not find workspace root (missing .cursor/audit-results). "
        "Run from the Kaggle/code workspace or pass --output explicitly."
    )


def resolve_audit_artifact_root(start: Path) -> Path:
    """Resolve audit artifact root like ``find_workspace_root`` without aborting.

    Falls back to the nearest ``.cursor`` directory, then ``start``'s directory,
    so degraded/skip precheck writers still emit next to repo tooling.
    """
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