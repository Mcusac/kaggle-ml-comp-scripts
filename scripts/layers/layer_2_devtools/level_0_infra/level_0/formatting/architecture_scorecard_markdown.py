"""Markdown scorecards built from existing health reports and audit manifests."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable

from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import (
    parse_generated_optional,
)
from layers.layer_2_devtools.level_0_infra.level_0.parse.json.report_json import (
    load_json_report,
)

from .health_report_views import (
    DEFAULT_COMPLEXITY_TARGET_NAMES,
    lines_complexity_targets,
    lines_duplication_summary,
    lines_srp_summary,
)


def _as_dict(obj: object) -> dict[str, Any]:
    return obj if isinstance(obj, dict) else {}


def _md_code_block(lines: Iterable[str]) -> list[str]:
    out = ["```"]
    out.extend([str(x).rstrip("\n") for x in lines])
    out.append("```")
    return out


def _md_kv_table(rows: list[tuple[str, str]]) -> list[str]:
    lines = ["| Field | Value |", "|------|-------|"]
    for k, v in rows:
        lines.append(f"| {k} | {v} |")
    return lines


def load_health_report(path: Path) -> dict[str, Any]:
    """Load a check_health JSON report."""
    return load_json_report(path)


def load_manifest(path: Path) -> dict[str, Any]:
    """Load either manifest v2 (audit orchestrator) or v1 (pipeline)."""
    return load_json_report(path)


@dataclass(frozen=True)
class ScorecardOptions:
    generated: date | None = None
    complexity_targets: list[str] | None = None
    top_duplicates: int = 20
    top_srp_modules: int = 20


def build_health_markdown_scorecard(
    health: dict[str, Any],
    *,
    report_path: Path,
    options: ScorecardOptions | None = None,
) -> str:
    opts = options or ScorecardOptions()
    generated = opts.generated
    if generated is None:
        generated = parse_generated_optional(None) or date.today()

    targets = opts.complexity_targets or list(DEFAULT_COMPLEXITY_TARGET_NAMES)

    lines: list[str] = [
        "---",
        f"generated: {generated.isoformat()}",
        "artifact: architecture_scorecard_health",
        f"source_report: {report_path.as_posix()}",
        "---",
        "",
        "# Architecture scorecard (health report)",
        "",
        "## Inputs",
        "",
    ]
    lines.extend(
        _md_kv_table(
            [
                ("health_report", f"`{report_path.as_posix()}`"),
                ("root", f"`{str(_as_dict(health).get('root', ''))}`"),
            ]
        )
    )

    lines.extend(["", "## Complexity targets", ""])
    lines.extend(
        _md_code_block(
            lines_complexity_targets(
                health,
                report_path=report_path,
                targets=list(targets),
            )
        )
    )

    lines.extend(["", "## SRP summary", ""])
    lines.extend(
        _md_code_block(
            lines_srp_summary(
                health,
                report_path=report_path,
                top_modules=int(opts.top_srp_modules),
            )
        )
    )

    lines.extend(["", "## Duplication summary", ""])
    lines.extend(
        _md_code_block(
            lines_duplication_summary(
                health,
                report_path=report_path,
                top=int(opts.top_duplicates),
            )
        )
    )
    lines.append("")
    return "\n".join(lines)


def _manifest_kind(manifest: dict[str, Any]) -> str:
    sv = str(manifest.get("schema_version") or "")
    if sv == "2":
        return "audit_orchestrator_manifest.v2"
    if sv:
        return f"manifest.v{sv}"
    if "aggregate" in manifest and "steps" in manifest:
        return "audit_orchestrator_manifest.unknown_version"
    if "aggregate" in manifest and "queue_summary" in manifest:
        return "code_audit_pipeline_manifest.unknown_version"
    return "manifest"


def build_manifest_markdown_scorecard(
    manifest: dict[str, Any],
    *,
    manifest_path: Path,
    generated: date | None = None,
) -> str:
    m = _as_dict(manifest)
    g = generated or parse_generated_optional(m.get("generated_date")) or date.today()
    kind = _manifest_kind(m)

    steps = m.get("steps")
    steps_d = steps if isinstance(steps, dict) else {}
    aggregate = _as_dict(m.get("aggregate"))

    lines: list[str] = [
        "---",
        f"generated: {g.isoformat()}",
        "artifact: architecture_scorecard_manifest",
        f"source_manifest: {manifest_path.as_posix()}",
        f"manifest_kind: {kind}",
        "---",
        "",
        "# Architecture scorecard (manifest)",
        "",
        "## Inputs",
        "",
    ]
    lines.extend(
        _md_kv_table(
            [
                ("manifest", f"`{manifest_path.as_posix()}`"),
                ("schema_version", f"`{m.get('schema_version', '')}`"),
                ("run_id", f"`{m.get('run_id', '')}`"),
                ("overall_exit_code", f"`{aggregate.get('overall_exit_code', '')}`"),
            ]
        )
    )

    lines.extend(["", "## Step summary", ""])
    lines.append("| Step | Status | Exit | Key metrics |")
    lines.append("|------|--------|------|------------|")
    for step_name in sorted(steps_d.keys()):
        rec = _as_dict(steps_d.get(step_name))
        status = str(rec.get("status") or "")
        exit_code = str(rec.get("exit_code") if rec.get("exit_code") is not None else "")
        metrics = rec.get("metrics")
        md_metrics = ""
        if isinstance(metrics, dict) and metrics:
            show = []
            for k in sorted(metrics.keys()):
                show.append(f"{k}={metrics[k]}")
            md_metrics = "`" + ", ".join(show[:8]) + "`"
        lines.append(f"| `{step_name}` | `{status}` | `{exit_code}` | {md_metrics} |")

    lines.extend(["", "## Artifacts (as recorded in manifest)", ""])
    any_artifacts = False
    for step_name in sorted(steps_d.keys()):
        rec = _as_dict(steps_d.get(step_name))
        artifacts = rec.get("artifacts")
        if not isinstance(artifacts, list) or not artifacts:
            continue
        any_artifacts = True
        lines.append(f"### {step_name}")
        lines.append("")
        for a in artifacts:
            row = _as_dict(a)
            kind_s = str(row.get("kind") or "")
            scope = str(row.get("scope") or "")
            md_path = str(row.get("md_path") or "")
            json_path = str(row.get("json_path") or "")
            rel_md = f"`{md_path}`" if md_path else ""
            rel_json = f"`{json_path}`" if json_path else ""
            tail = " ".join([x for x in [rel_md, rel_json] if x]).strip()
            lines.append(f"- **{kind_s}** ({scope}) {tail}".rstrip())
        lines.append("")
    if not any_artifacts:
        lines.append("_No artifacts recorded in this manifest._")
        lines.append("")

    return "\n".join(lines)

