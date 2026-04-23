#!/usr/bin/env python3
"""CI runner: fast checks (pipeline + scans + health + thresholds) with artifacts + summary.

Run from ``kaggle-ml-comp-scripts/scripts/``::

  python -m layers.layer_2_devtools.level_1_impl.level_2.ci_runner --run-id local-test --strict --fail-on-skipped
"""

from __future__ import annotations

import argparse
import io
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_SCRIPTS_ROOT = _SCRIPT_DIR.parents[3]
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_1.api_ci import run_ci_runner


def _win_utf8_stdio() -> None:
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def _default_run_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    return f"local-{stamp}"


def _write_step_summary(*, lines: list[str], enabled: bool) -> None:
    if not enabled:
        return
    target = os.environ.get("GITHUB_STEP_SUMMARY")
    if not target:
        return
    try:
        with open(target, "a", encoding="utf-8") as f:
            f.write("\n".join(lines).rstrip() + "\n")
    except OSError as exc:
        print(f"⚠️ [WARN] Failed to write GitHub step summary: {exc}", file=sys.stderr)


def _summary_lines(data: dict) -> list[str]:
    overall = int(data.get("overall_exit_code", 1))
    header = "✅ CI Runner: PASS" if overall == 0 else "❌ CI Runner: FAIL"
    lines = [f"## {header}", ""]
    lines.append(f"- **run_id**: `{data.get('run_id')}`")
    if data.get("manifest_path"):
        lines.append(f"- **manifest**: `{data.get('manifest_path')}`")
    if data.get("health_report_path"):
        lines.append(f"- **health_report**: `{data.get('health_report_path')}`")
    lines.append("")
    lines.append("### Steps")
    for step in data.get("steps", []):
        name = step.get("name")
        rc = int(step.get("exit_code", 0))
        status = "✅" if rc == 0 else "❌"
        lines.append(f"- {status} **{name}** (exit_code={rc})")
        if step.get("summary_line"):
            lines.append(f"  - `{step.get('summary_line')}`")
        if step.get("md_path"):
            lines.append(f"  - md: `{step.get('md_path')}`")
        if step.get("json_path"):
            lines.append(f"  - json: `{step.get('json_path')}`")
        if step.get("manifest_path"):
            lines.append(f"  - manifest: `{step.get('manifest_path')}`")
        if step.get("errors"):
            lines.append(f"  - errors: `{'; '.join(step.get('errors', []))}`")
    lines.append("")
    return lines


def _write_runner_summary_file(*, workspace_root: Path, run_id: str, lines: list[str]) -> Path:
    out_dir = (
        workspace_root
        / ".cursor"
        / "audit-results"
        / "general"
        / "summaries"
        / "ci_runs"
        / run_id
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "summary.md"
    out_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return out_path


def _write_health_pretty_json(health_report_path: Path) -> Path:
    pretty = health_report_path.with_name("health_report_pretty.json")
    data = json.loads(health_report_path.read_text(encoding="utf-8"))
    pretty.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return pretty


def main() -> int:
    _win_utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    default_workspace = _SCRIPTS_ROOT.parent
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=default_workspace,
        help="Repository root (artifact base; default: ../ from scripts/).",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Run id for manifest + summary (default: local-<utc-timestamp>).",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="YYYY-MM-DD for scan filenames (default: today).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Strict mode: fail health warnings and fail parse errors in scans.",
    )
    parser.add_argument(
        "--fail-on-skipped",
        action="store_true",
        help="Fail if any enabled pipeline step ends with status skipped.",
    )
    parser.add_argument(
        "--health-root",
        type=Path,
        default=None,
        help="Root for health checks (default: --workspace-root).",
    )
    parser.add_argument(
        "--health-report",
        type=Path,
        default=None,
        help="Health report JSON path (default: <workspace-root>/health_report.json).",
    )
    parser.add_argument(
        "--threshold-config",
        type=Path,
        default=None,
        help="Optional thresholds config JSON for health.",
    )
    parser.add_argument(
        "--github-summary",
        action="store_true",
        help="Write a summary to $GITHUB_STEP_SUMMARY when available.",
    )
    parser.add_argument(
        "--no-github-summary",
        action="store_true",
        help="Disable summary even if $GITHUB_STEP_SUMMARY is set.",
    )
    args = parser.parse_args()

    workspace_root = args.workspace_root.resolve()
    run_id = str(args.run_id or _default_run_id())
    health_root = (args.health_root or workspace_root).resolve()
    health_report_path = (args.health_report or (workspace_root / "health_report.json")).resolve()

    env = run_ci_runner(
        {
            "scripts_root": _SCRIPTS_ROOT,
            "workspace_root": workspace_root,
            "run_id": run_id,
            "generated": args.date,
            "strict": bool(args.strict),
            "fail_on_skipped": bool(args.fail_on_skipped),
            "health_root": health_root,
            "health_report_path": health_report_path,
            "threshold_config_path": args.threshold_config.resolve() if args.threshold_config else None,
        }
    )
    if env["status"] != "ok":
        print(f"❌ Error: {'; '.join(env['errors'])}", file=sys.stderr)
        return 2

    data = env["data"]
    try:
        pretty = _write_health_pretty_json(health_report_path)
        data["health_report_pretty_path"] = str(pretty)
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(f"⚠️ [WARN] Failed to pretty-print health report: {exc}", file=sys.stderr)

    lines = _summary_lines(data)
    summary_path = _write_runner_summary_file(
        workspace_root=workspace_root,
        run_id=run_id,
        lines=lines,
    )
    print(f"✅ [OK] Wrote CI summary: {summary_path}")

    enabled = bool(args.github_summary) and (not bool(args.no_github_summary))
    _write_step_summary(lines=lines, enabled=enabled)

    overall = int(data.get("overall_exit_code", 1))
    if overall == 0:
        print("✅ [OK] CI runner completed successfully.")
    else:
        print("❌ [FAIL] CI runner detected failures.", file=sys.stderr)
    return overall


if __name__ == "__main__":
    raise SystemExit(main())

