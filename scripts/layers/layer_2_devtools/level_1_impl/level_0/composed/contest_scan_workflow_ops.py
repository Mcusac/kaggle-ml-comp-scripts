"""Contest tier scan composed workflow."""

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_1_impl.level_0.scan.contest_scan_ops import (
    scan_contest_level_directory,
)
from layers.layer_2_devtools.level_0_infra.level_0.constants.import_patterns import LEVEL_DIR_RE
from layers.layer_2_devtools.level_0_infra.level_0.path.workspace import find_workspace_root


@dataclass(frozen=True)
class ContestTierScanResult:
    reports: list
    payload: dict[str, Any]
    markdown: str
    workspace: Path


def run_contest_tier_scan_workflow(
    *,
    scripts_dir: Path,
    contest_root: Path,
    contest_slug: str,
    generated: date,
    workspace_root: Path | None = None,
) -> ContestTierScanResult:
    """Run contest tier scan across all level_K directories."""
    root = contest_root.resolve()
    workspace = (
        workspace_root.resolve() if workspace_root else find_workspace_root(scripts_dir.resolve())
    )
    reports: list = []
    for child in sorted(root.iterdir()):
        if child.is_dir() and LEVEL_DIR_RE.fullmatch(child.name):
            reports.extend(
                scan_contest_level_directory(
                    root,
                    child,
                    contest_slug,
                    forbid_relative_in_logic=False,
                )
            )
    upward = [
        {"path": str(report.path), "line": v.line, "detail": v.detail}
        for report in reports
        for v in report.violations
        if v.kind == "CONTEST_UPWARD"
    ]
    other = [
        {"path": str(report.path), "line": v.line, "kind": v.kind, "detail": v.detail}
        for report in reports
        for v in report.violations
        if v.kind != "CONTEST_UPWARD"
    ]
    payload = {
        "contest_root": str(root),
        "generated": generated.isoformat(),
        "files": len(reports),
        "contest_upward": upward,
        "other_violations": other,
    }
    markdown = _build_markdown(root, reports, generated, len(upward), len(other))
    return ContestTierScanResult(
        reports=reports,
        payload=payload,
        markdown=markdown,
        workspace=workspace,
    )


def _build_markdown(
    contest_root: Path,
    reports: list,
    generated: date,
    upward_count: int,
    other_count: int,
) -> str:
    lines = [
        f"# Contest tier import scan ({generated.isoformat()})",
        "",
        f"- Contest root: `{contest_root}`",
        f"- Files scanned: {len(reports)}",
        f"- **CONTEST_UPWARD** (level_M with M >= K): **{upward_count}**",
        f"- Other violations: {other_count}",
        "",
    ]
    upward = [
        (report.path, violation)
        for report in reports
        for violation in report.violations
        if violation.kind == "CONTEST_UPWARD"
    ]
    if upward:
        lines.append("## CONTEST_UPWARD")
        lines.append("")
        for path, violation in upward:
            lines.append(f"- `{path}` line {violation.line}: {violation.detail}")
        lines.append("")
    return "\n".join(lines) + "\n"