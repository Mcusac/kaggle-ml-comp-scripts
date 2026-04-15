"""General stack scan composed workflow and violation-fix follow-up."""

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_1_impl.level_0.scan.general_scan_ops import (
    build_general_json_payload,
    build_general_markdown,
    iter_level_py_files,
    scan_general_stack_file,
)
from layers.layer_2_devtools.level_0_infra.level_0.fix.violation_fix_bundle import (
    run_violation_fix_bundle,
)
from layers.layer_2_devtools.level_0_infra.level_0 import (
    format_scan_violation_summary_lines,
)
from layers.layer_2_devtools.level_0_infra.level_0.io.json_fs import (
    latest_path_by_glob_mtime,
    read_json_object,
)
from layers.layer_2_devtools.level_0_infra.level_0.path.workspace import find_workspace_root


@dataclass(frozen=True)
class GeneralScanRunResult:
    files: list[Path]
    reports: list
    markdown: str
    payload: dict[str, Any]
    workspace: Path


def run_general_scan_workflow(
    scripts_dir: Path,
    *,
    generated: date,
    workspace_root: Path | None = None,
) -> GeneralScanRunResult:
    """Execute full general-stack scan and return structured outputs."""
    root = scripts_dir.resolve()
    workspace = workspace_root.resolve() if workspace_root else find_workspace_root(root)
    files = iter_level_py_files(root)
    reports = [scan_general_stack_file(path, root) for path in files]
    markdown = build_general_markdown(reports, generated, root, workspace)
    payload = build_general_json_payload(reports, generated, root, workspace)
    return GeneralScanRunResult(files, reports, markdown, payload, workspace)


@dataclass
class ViolationFixWorkflowOptions:
    json_path: Path | None
    audits_dir: Path | None
    apply: bool
    verify: bool
    scripts_dev_dir: Path
    scripts_root: Path


def _write_general_stack_scan_outputs(scripts_root: Path) -> None:
    default_scripts = (scripts_root / "layers" / "layer_0_core").resolve()
    generated = date.today()
    result = run_general_scan_workflow(
        default_scripts, generated=generated, workspace_root=None
    )
    workspace = result.workspace
    out_dir = workspace / ".cursor/audit-results/general/audits"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"level_violations_scan_{generated.isoformat()}.md"
    files = result.files
    reports = result.reports
    md = result.markdown
    out_path.write_text(md, encoding="utf-8")
    print(f"[OK] Wrote {out_path}")
    payload = result.payload
    json_path = out_path.with_suffix(".json")
    json_path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"[OK] Wrote {json_path}")
    total_v = sum(len(r.violations) for r in reports)
    pe = sum(1 for r in reports if r.parse_error)
    print(
        f"[SUMMARY] Files scanned: {len(files)} | "
        f"Violations: {total_v} | Parse errors: {pe}"
    )


def run_violation_fix_workflow(opts: ViolationFixWorkflowOptions) -> None:
    workspace = find_workspace_root(opts.scripts_dev_dir.resolve())
    audits_dir = (
        opts.audits_dir.resolve()
        if opts.audits_dir
        else workspace / ".cursor/audit-results/general/audits"
    )
    try:
        jpath = (
            opts.json_path.resolve()
            if opts.json_path
            else latest_path_by_glob_mtime(audits_dir, "level_violations_scan_*.json")
        )
    except FileNotFoundError as exc:
        raise SystemExit(str(exc)) from exc
    data = read_json_object(jpath)
    for line in format_scan_violation_summary_lines(data):
        print(line)
    dry_run = not opts.apply
    if dry_run:
        print("\n[DRY-RUN] Re-run with --apply to execute bundled fixes.")
    print(
        f"[RUN] violation_fix_bundle (scripts_dev_dir={opts.scripts_dev_dir}, "
        f"dry_run={dry_run})"
    )
    run_violation_fix_bundle(opts.scripts_dev_dir, dry_run)
    if opts.verify and opts.apply:
        _write_general_stack_scan_outputs(opts.scripts_root.resolve())