"""Deterministic paths under .cursor/audit-results."""

from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path


def precheck_summary_json_path(
    workspace: Path,
    audit_scope: str,
    level_name: str,
    generated: date,
) -> Path:
    """Path to precheck JSON for one target and date."""
    return (
        workspace
        / ".cursor"
        / "audit-results"
        / audit_scope
        / "summaries"
        / f"precheck_{level_name}_{generated.isoformat()}.json"
    )


def run_snapshot_level_dir(
    workspace: Path,
    audit_scope: str,
    level_name: str,
    generated: date,
) -> Path:
    """Dated run snapshot folder for one target (alongside canonical inventories/audits)."""
    return (
        workspace.resolve()
        / ".cursor"
        / "audit-results"
        / audit_scope
        / "runs"
        / generated.isoformat()
        / level_name
    )


def mirror_files_to_run_snapshot(
    *,
    workspace: Path,
    audit_scope: str,
    level_name: str,
    generated: date,
    sources: list[Path],
) -> list[Path]:
    """Copy files into ``runs/<date>/<level_name>/`` preserving basenames."""
    dest_dir = run_snapshot_level_dir(workspace, audit_scope, level_name, generated)
    dest_dir.mkdir(parents=True, exist_ok=True)
    out: list[Path] = []
    for src in sources:
        if not src.is_file():
            continue
        target = dest_dir / src.name
        shutil.copy2(src, target)
        out.append(target)
    return out


def architecture_scorecard_markdown_path(
    workspace: Path,
    audit_scope: str,
    generated: date,
    *,
    stem: str = "architecture_scorecard",
) -> Path:
    """Path for a consolidated markdown scorecard under summaries/."""
    safe_stem = stem.strip() or "architecture_scorecard"
    return (
        workspace
        / ".cursor"
        / "audit-results"
        / audit_scope
        / "summaries"
        / f"{safe_stem}_{generated.isoformat()}.md"
    )


def architecture_score_json_path(
    workspace: Path,
    audit_scope: str,
    generated: date,
    *,
    stem: str = "architecture_score",
) -> Path:
    """Path for a consolidated score JSON under summaries/."""
    safe_stem = stem.strip() or "architecture_score"
    return (
        workspace
        / ".cursor"
        / "audit-results"
        / audit_scope
        / "summaries"
        / f"{safe_stem}_{generated.isoformat()}.json"
    )