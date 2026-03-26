"""Deterministic paths under .cursor/audit-results."""

from __future__ import annotations

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


__all__ = ["precheck_summary_json_path"]
