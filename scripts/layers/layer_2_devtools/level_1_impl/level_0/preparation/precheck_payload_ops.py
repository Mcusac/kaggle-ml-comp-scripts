"""Composed precheck payload operations using level_0 primitives."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from layers.layer_2_devtools.level_0_infra.level_0.models.audit_models import FileReport


@dataclass
class PrecheckMeta:
    generated: date
    audit_scope: str
    level_name: str
    artifact: str
    scan_root: Path


def build_precheck_markdown(
    reports: list[FileReport],
    meta: PrecheckMeta,
    workspace: Path,
    title: str,
    kinds_order: list[str],
) -> str:
    """Build markdown precheck artifact content."""
    lines = [
        "---",
        f"generated: {meta.generated.isoformat()}",
        f"scope: {meta.audit_scope}",
        f"level: {meta.level_name}",
        f"artifact: {meta.artifact}",
        "---",
        "",
        f"# {title}",
        "",
        f"**Scan root:** `{meta.scan_root.as_posix()}`",
        "",
        "## Summary",
        "",
    ]
    for kind in kinds_order:
        if kind == "PARSE_ERROR":
            count = sum(1 for report in reports if report.parse_error)
        else:
            count = sum(1 for report in reports if any(v.kind == kind for v in report.violations))
        lines.append(f"- **{kind}:** {count} file(s)")
    lines.append("")

    for kind in kinds_order:
        if kind == "PARSE_ERROR":
            bad = [report for report in reports if report.parse_error]
            if not bad:
                continue
            lines.append(f"## {kind}")
            lines.append("")
            for report in sorted(bad, key=lambda item: str(item.path)):
                rel = report.path.relative_to(workspace)
                lines.append(f"- `{rel.as_posix()}` — {report.parse_error}")
            lines.append("")
            continue
        files_with = [report for report in reports if any(v.kind == kind for v in report.violations)]
        if not files_with:
            continue
        lines.append(f"## {kind}")
        lines.append("")
        for report in sorted(files_with, key=lambda item: str(item.path)):
            rel = report.path.relative_to(workspace)
            lines.append(f"### `{rel.as_posix()}`")
            lines.append("")
            for violation in [v for v in report.violations if v.kind == kind]:
                lines.append(f"- Line {violation.line}: {violation.detail}")
            lines.append("")

    lines.append("## Clean files")
    lines.append("")
    clean = [report for report in reports if not report.parse_error and not report.violations]
    if not clean:
        lines.append("_None._")
    else:
        for report in sorted(clean, key=lambda item: str(item.path)):
            rel = report.path.relative_to(workspace)
            lines.append(f"- `{rel.as_posix()}`")
    lines.append("")
    return "\n".join(lines)


def build_precheck_json(
    reports: list[FileReport],
    meta: PrecheckMeta,
    workspace: Path,
) -> dict:
    """Build normalized precheck JSON payload."""
    violations: list[dict] = []
    parse_errors: list[dict] = []
    for report in reports:
        rel_file = report.path.relative_to(workspace).as_posix()
        if report.parse_error:
            parse_errors.append({"file": rel_file, "detail": report.parse_error})
            continue
        for violation in report.violations:
            violations.append(
                {
                    "file": rel_file,
                    "kind": violation.kind,
                    "line": violation.line,
                    "detail": violation.detail,
                }
            )
    return {
        "generated": meta.generated.isoformat(),
        "scope": meta.audit_scope,
        "level": meta.level_name,
        "artifact": meta.artifact,
        "scan_root": str(meta.scan_root.resolve()),
        "violations": violations,
        "parse_errors": parse_errors,
    }


def dumps_json(payload: dict) -> str:
    """Dump payload JSON with deterministic formatting."""
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


__all__ = ["PrecheckMeta", "build_precheck_markdown", "build_precheck_json", "dumps_json"]
