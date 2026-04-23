"""Merge general, contest, and competition-infra import scans for barrel-style enforcement."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_0_infra.level_0.constants.import_patterns import LEVEL_DIR_RE
from layers.layer_2_devtools.level_0_infra.level_0.models.audit_models import FileReport
from layers.layer_2_devtools.level_1_impl.level_0.composed.contest_scan_workflow_ops import (
    run_contest_tier_scan_workflow,
)
from layers.layer_2_devtools.level_1_impl.level_0.composed.general_scan_workflow_ops import (
    run_general_scan_workflow,
)
from layers.layer_2_devtools.level_1_impl.level_0.scan.general_scan_ops import build_general_json_payload
from layers.layer_2_devtools.level_1_impl.level_0.scan.infra_scan_ops import (
    scan_infra_level_directory,
)


def iter_infra_tier_level_dirs(infra_level_0: Path) -> list[Path]:
    """``level_0`` root under ``level_0_infra``; child dirs named ``level_K`` only."""
    root = infra_level_0.resolve()
    if not root.is_dir():
        return []
    return sorted(
        c for c in root.iterdir() if c.is_dir() and LEVEL_DIR_RE.fullmatch(c.name)
    )


def run_full_infra_stack_scan(*, infra_level_0: Path) -> list[FileReport]:
    """Scan all ``level_K`` package dirs under ``.../level_0_infra/level_0``."""
    reports: list[FileReport] = []
    for d in iter_infra_tier_level_dirs(infra_level_0):
        reports.extend(scan_infra_level_directory(d))
    return reports


def build_infra_json_friendly(
    reports: list[FileReport], workspace: Path, generated: date, infra_level_0: Path
) -> dict[str, Any]:
    """Payload fragment mirroring :func:`build_general_json_payload` shape (no top-level ``schema``)."""
    violations: list[dict[str, Any]] = []
    parse_errors: list[dict[str, str]] = []
    ws = workspace.resolve()
    for report in reports:
        try:
            rel_file = report.path.resolve().relative_to(ws).as_posix()
        except ValueError:
            rel_file = str(report.path.resolve())
        if report.parse_error:
            parse_errors.append({"file": rel_file, "detail": str(report.parse_error)})
            continue
        for v in report.violations:
            violations.append(
                {
                    "file": rel_file,
                    "kind": v.kind,
                    "line": v.line,
                    "detail": v.detail,
                }
            )
    return {
        "generated": generated.isoformat(),
        "scope": "infra",
        "artifact": "barrel_enforcement_infra_component",
        "infra_level_0_root": str(infra_level_0.resolve()),
        "files_scanned": len(reports),
        "violations": violations,
        "parse_errors": parse_errors,
    }


def _rel_file(path: Path, workspace: Path) -> str:
    try:
        return path.resolve().relative_to(workspace.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def merge_barrel_violation_rows(
    *,
    general_payload: dict[str, Any],
    contest_payload: dict[str, Any] | None,
    infra_fragment: dict[str, Any] | None,
    workspace: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Flatten per-scope payloads into one violation list and one parse_error list (each with ``scope``)."""
    out_v: list[dict[str, Any]] = []
    out_pe: list[dict[str, Any]] = []
    for row in general_payload.get("violations", []):
        e = {**row, "scope": "general"}
        out_v.append(e)
    for row in general_payload.get("parse_errors", []):
        e = {**row, "scope": "general"}
        out_pe.append(e)
    if contest_payload:
        for item in contest_payload.get("contest_upward", []):
            out_v.append(
                {
                    "scope": "contest",
                    "file": item.get("path", ""),
                    "line": item.get("line", 0),
                    "kind": "CONTEST_UPWARD",
                    "detail": item.get("detail", ""),
                }
            )
        for item in contest_payload.get("other_violations", []):
            out_v.append(
                {
                    "scope": "contest",
                    "file": item.get("path", ""),
                    "line": item.get("line", 0),
                    "kind": item.get("kind", ""),
                    "detail": item.get("detail", ""),
                }
            )
    if infra_fragment:
        for row in infra_fragment.get("violations", []):
            e = {**row, "scope": "infra"}
            out_v.append(e)
        for row in infra_fragment.get("parse_errors", []):
            e = {**row, "scope": "infra"}
            out_pe.append(e)
    def _norm_file(row: dict[str, Any]) -> None:
        f = row.get("file", "")
        if not f:
            return
        p = Path(str(f))
        try:
            p = p.resolve() if p.is_absolute() else (workspace / f).resolve()
            row["file"] = _rel_file(p, workspace)
        except (OSError, TypeError, ValueError):
            pass

    for row in out_v:
        _norm_file(row)
    for row in out_pe:
        _norm_file(row)
    return out_v, out_pe


def build_merged_barrel_enforcement_payload(
    *,
    generated: date,
    workspace: Path,
    scripts_root: Path,
    general_payload: dict[str, Any],
    contest_payload: dict[str, Any] | None,
    infra_fragment: dict[str, Any] | None,
) -> dict[str, Any]:
    """Unified JSON: ``barrel_enforcement_scan.v1`` with embedded components."""
    v_rows, pe_rows = merge_barrel_violation_rows(
        general_payload=general_payload,
        contest_payload=contest_payload,
        infra_fragment=infra_fragment,
        workspace=workspace,
    )
    def _count_scope(scope: str) -> dict[str, int]:
        v = [r for r in v_rows if r.get("scope") == scope]
        p = [r for r in pe_rows if r.get("scope") == scope]
        return {"violations": len(v), "parse_errors": len(p)}

    return {
        "schema": "barrel_enforcement_scan.v1",
        "generated": generated.isoformat(),
        "workspace": str(workspace.resolve()),
        "scripts_root": str(scripts_root.resolve()),
        "violation_count": len(v_rows),
        "parse_error_count": len(pe_rows),
        "violations": v_rows,
        "parse_errors": pe_rows,
        "by_scope": {
            "general": _count_scope("general"),
            "contest": _count_scope("contest"),
            "infra": _count_scope("infra"),
        },
        "components": {
            "general": {
                "schema": general_payload.get("schema"),
                "scripts_dir": general_payload.get("scripts_dir"),
            },
            "contest": (
                {
                    k: contest_payload[k]
                    for k in ("contest_root", "files", "generated")
                    if contest_payload and k in contest_payload
                }
                if contest_payload
                else None
            ),
            "infra": (
                {
                    "infra_level_0_root": infra_fragment.get("infra_level_0_root"),
                    "files_scanned": infra_fragment.get("files_scanned"),
                }
                if infra_fragment
                else None
            ),
        },
    }


def _section_lines(
    title: str, scope: str, rows: list[dict[str, Any]], kinds_order: list[str] | None = None
) -> list[str]:
    lines: list[str] = [f"## {title}", ""]
    scope_rows = [r for r in rows if r.get("scope") == scope]
    if not scope_rows:
        lines.append(f"_No violations in **{title}** scope._")
        lines.append("")
        return lines
    if kinds_order:
        kinds_set = set(kinds_order)
        for kind in kinds_order:
            sub = [r for r in scope_rows if r.get("kind") == kind]
            if not sub:
                continue
            lines.append(f"### {kind}")
            lines.append("")
            for r in sorted(sub, key=lambda x: (str(x.get("file")), int(x.get("line") or 0))):
                fn = r.get("file", "")
                ln = r.get("line", 0)
                det = r.get("detail", "")
                lines.append(f"- `{fn}` line {ln}: {det}")
            lines.append("")
        other = [r for r in scope_rows if r.get("kind") not in kinds_set]
        if other:
            lines.append("### Other")
            lines.append("")
            for r in sorted(
                other, key=lambda x: (str(x.get("file")), int(x.get("line") or 0))
            ):
                k = r.get("kind", "")
                fn = r.get("file", "")
                ln = r.get("line", 0)
                det = r.get("detail", "")
                lines.append(f"- **{k}** `{fn}` line {ln}: {det}")
            lines.append("")
    else:
        for r in sorted(
            scope_rows, key=lambda x: (str(x.get("file")), int(x.get("line") or 0))
        ):
            kind = r.get("kind", "")
            fn = r.get("file", "")
            ln = r.get("line", 0)
            det = r.get("detail", "")
            if kind:
                lines.append(f"- **{kind}** `{fn}` line {ln}: {det}")
            else:
                lines.append(f"- `{fn}` line {ln}: {det}")
        lines.append("")
    return lines


def build_barrel_enforcement_markdown(merged: dict[str, Any]) -> str:
    """Human-readable report from a merged v1 payload."""
    gen = merged.get("generated", "")
    vcount = merged.get("violation_count", 0)
    pec = merged.get("parse_error_count", 0)
    lines = [
        f"# Barrel enforcement scan ({gen})",
        "",
        f"- **Schema:** `{merged.get('schema', '')}`",
        f"- **Workspace:** `{merged.get('workspace', '')}`",
        f"- **Total violations (all scopes):** {vcount}",
        f"- **Parse errors (all scopes):** {pec}",
        "",
    ]
    gkinds = [
        "LAYER0_CORE_MIXED_IMPORT_STYLE",
        "WRONG_LEVEL",
        "UPWARD",
        "DEEP_PATH",
        "RELATIVE_IN_LOGIC",
    ]
    ckinds = [
        "CONTEST_UPWARD",
        "CONTEST_DEEP_PATH",
        "CONTEST_OTHER_PACKAGE",
        "RELATIVE_IN_LOGIC",
    ]
    ikinds = [
        "INFRA_TIER_UPWARD",
        "INFRA_BARREL_DEEP",
        "INFRA_GENERAL_LEVEL",
        "DEEP_PATH",
        "RELATIVE_IN_LOGIC",
    ]
    rows = [r for r in merged.get("violations", []) if isinstance(r, dict)]
    lines.extend(_section_lines("General stack (`layer_0_core`)", "general", rows, gkinds))
    lines.extend(_section_lines("Contest tree", "contest", rows, ckinds))
    lines.extend(
        _section_lines("Competition infra (`level_0_infra`)", "infra", rows, ikinds)
    )
    pe = [r for r in merged.get("parse_errors", []) if isinstance(r, dict)]
    if pe:
        lines.append("## Parse errors")
        lines.append("")
        for r in pe:
            lines.append(
                f"- **{r.get('scope', '')}** `{r.get('file', '')}`: {r.get('detail', '')}"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


@dataclass(frozen=True)
class BarrelEnforcementRun:
    """End-to-end in-memory result before writing artifacts."""

    merged: dict[str, Any]
    markdown: str
    workspace: Path
    general_payload: dict[str, Any]
    contest_payload: dict[str, Any] | None
    infra_fragment: dict[str, Any] | None


def run_barrel_enforcement_workflow(
    *,
    layer_0_core: Path,
    scripts_root: Path,
    generated: date,
    contest_root: Path | None,
    contest_slug: str,
    infra_level_0: Path | None,
    run_general: bool = True,
    run_contest: bool = True,
    run_infra: bool = True,
    workspace_root: Path | None = None,
) -> BarrelEnforcementRun:
    """Run selected scans and merge. Paths must exist where used."""
    general_payload: dict[str, Any] = {}
    contest_payload: dict[str, Any] | None = None
    infra_fragment: dict[str, Any] | None = None
    workspace: Path

    if run_general:
        g = run_general_scan_workflow(
            layer_0_core.resolve(), generated=generated, workspace_root=workspace_root
        )
        workspace = g.workspace
        general_payload = build_general_json_payload(
            g.reports, generated, layer_0_core.resolve(), g.workspace
        )
    else:
        from layers.layer_2_devtools.level_0_infra.level_0.path.workspace import (  # local import
            find_workspace_root,
        )

        anchor = (workspace_root or contest_root or infra_level_0 or layer_0_core).resolve()
        workspace = find_workspace_root(anchor)
        general_payload = {
            "generated": generated.isoformat(),
            "scope": "general",
            "schema": "level_violations_scan.v2",
            "scripts_dir": str(layer_0_core.resolve()),
            "violations": [],
            "parse_errors": [],
        }

    if run_contest and contest_root is not None and contest_root.is_dir():
        c = run_contest_tier_scan_workflow(
            scripts_dir=scripts_root.resolve(),
            contest_root=contest_root,
            contest_slug=contest_slug,
            generated=generated,
            workspace_root=workspace_root,
        )
        d = c.payload
        contest_payload = {
            "contest_root": d.get("contest_root"),
            "files": d.get("files"),
            "generated": d.get("generated"),
            "contest_upward": d.get("contest_upward", []),
            "other_violations": d.get("other_violations", []),
        }
        if not run_general:
            workspace = c.workspace

    if run_infra and infra_level_0 is not None and infra_level_0.is_dir():
        infra_reports = run_full_infra_stack_scan(infra_level_0=infra_level_0)
        infra_fragment = build_infra_json_friendly(
            infra_reports, workspace, generated, infra_level_0
        )

    merged = build_merged_barrel_enforcement_payload(
        generated=generated,
        workspace=workspace,
        scripts_root=scripts_root,
        general_payload=general_payload,
        contest_payload=contest_payload,
        infra_fragment=infra_fragment,
    )
    md = build_barrel_enforcement_markdown(merged)
    return BarrelEnforcementRun(
        merged=merged,
        markdown=md,
        workspace=workspace,
        general_payload=general_payload,
        contest_payload=contest_payload,
        infra_fragment=infra_fragment,
    )
