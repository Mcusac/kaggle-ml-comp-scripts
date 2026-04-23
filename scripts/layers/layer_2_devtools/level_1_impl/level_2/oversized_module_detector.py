#!/usr/bin/env python3
"""
Oversized module detector for Python packages under a chosen root.

Reuses the existing health analyzer `FileMetricsAnalyzer` and threshold config
(`ThresholdConfig.max_file_lines`) to produce a focused report with
conservative split suggestions.

Usage (cwd ``kaggle-ml-comp-scripts/scripts/``)::
  python -m layers.layer_2_devtools.level_1_impl.level_2.oversized_module_detector --help
"""

import argparse
import io
import json
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
_SCRIPTS_ROOT = _SCRIPT_DIR.parents[3]
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_0_infra.level_0.formatting.health_report_views import (
    lines_oversized_modules,
)
from layers.layer_2_devtools.level_0_infra.level_0.health_thresholds import ThresholdConfig
from layers.layer_2_devtools.level_0_infra.level_1.health_analyzers.file_metrics import (
    FileMetricsAnalyzer,
)
from layers.layer_2_devtools.level_0_infra.level_0.path.workspace import (
    resolve_workspace_root,
)


def _win_utf8_stdio() -> None:
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def _load_threshold_config(path: Path | None) -> ThresholdConfig:
    config = ThresholdConfig()
    if path and path.is_file():
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, dict):
            config = ThresholdConfig.from_dict(data)
    return config


def _safe_int(x: object, default: int = 0) -> int:
    try:
        return int(x)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class OversizedModuleRow:
    module: str
    lines: int


def _extract_oversized_rows(metrics: dict[str, Any], *, max_file_lines: int) -> list[OversizedModuleRow]:
    long_files = metrics.get("long_files", [])
    if not isinstance(long_files, list):
        return []
    rows: list[OversizedModuleRow] = []
    for r in long_files:
        if not isinstance(r, dict):
            continue
        module = str(r.get("module") or "")
        if not module:
            continue
        lines = _safe_int(r.get("lines"))
        if lines > max(0, int(max_file_lines)):
            rows.append(OversizedModuleRow(module=module, lines=lines))
    rows.sort(key=lambda x: (-x.lines, x.module))
    return rows


def _write_artifacts(
    *,
    workspace: Path,
    output_dir: Path,
    generated: date,
    root: Path,
    threshold_config_path: Path | None,
    max_file_lines: int,
    top: int,
    include_suggestions: bool,
    metrics: dict[str, Any],
    oversized: list[OversizedModuleRow],
    write_json: bool,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    stem = f"oversized_module_scan_{generated.isoformat()}"
    md_path = output_dir / f"{stem}.md"

    report_data: dict[str, Any] = {
        "root": str(root.resolve()),
        "file_metrics": metrics,
    }
    body_lines = lines_oversized_modules(
        report_data,
        report_path=md_path,
        max_file_lines=max_file_lines,
        top=top,
        include_suggestions=include_suggestions,
    )

    header = [
        "---",
        f"generated: {generated.isoformat()}",
        "artifact: oversized_module_scan",
        "schema: oversized_module_scan.v1",
        f"root: {root.resolve().as_posix()}",
        f"max_file_lines: {max_file_lines}",
        f"oversized_count: {len(oversized)}",
        f"threshold_config_path: {(threshold_config_path.resolve().as_posix() if threshold_config_path else None)}",
        "---",
        "",
        "# Oversized module scan",
        "",
        f"- Root: `{root.resolve().as_posix()}`",
        f"- Threshold: max_file_lines={max_file_lines}",
        f"- Oversized modules: {len(oversized)}",
        "",
    ]

    md_path.write_text("\n".join([*header, *body_lines]).rstrip("\n") + "\n", encoding="utf-8")
    out: dict[str, Any] = {
        "md_path": str(md_path),
        "oversized_count": len(oversized),
        "max_file_lines": max_file_lines,
    }

    if write_json:
        payload = {
            "schema": "oversized_module_scan.v1",
            "generated": generated.isoformat(),
            "workspace": workspace.as_posix(),
            "root": root.resolve().as_posix(),
            "max_file_lines": max_file_lines,
            "oversized_count": len(oversized),
            "oversized": [{"module": r.module, "lines": r.lines} for r in oversized],
            "file_metrics": metrics,
        }
        json_path = output_dir / f"{stem}.json"
        json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        out["json_path"] = str(json_path)

    return out


def main() -> int:
    _win_utf8_stdio()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=_SCRIPTS_ROOT,
        help="Root directory to analyze (default: scripts/).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Write artifacts here (default: <workspace>/.cursor/audit-results/general/audits).",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="YYYY-MM-DD for filenames (default: today).",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=None,
        help="Threshold config JSON (same shape as ThresholdConfig.to_dict()).",
    )
    parser.add_argument(
        "--max-file-lines",
        type=int,
        default=None,
        help="Override max_file_lines (otherwise from config/default).",
    )
    parser.add_argument("--top", type=int, default=50, help="Show top N oversized modules.")
    parser.add_argument(
        "--no-suggestions",
        action="store_true",
        help="Do not emit split suggestions (report still lists oversized modules).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Also write oversized_module_scan_<date>.json next to the .md report.",
    )
    parser.add_argument(
        "--fail-on-oversized",
        action="store_true",
        help="Exit 1 if oversized_count exceeds --max-oversized (default 0).",
    )
    parser.add_argument(
        "--max-oversized",
        type=int,
        default=0,
        help="When using --fail-on-oversized, allow up to this many oversized modules.",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    generated = date.fromisoformat(args.date) if args.date else date.today()
    workspace = resolve_workspace_root(root)

    threshold_cfg = _load_threshold_config(args.config.resolve() if args.config else None)
    max_file_lines = (
        int(args.max_file_lines)
        if args.max_file_lines is not None
        else int(getattr(threshold_cfg, "max_file_lines", 500))
    )

    output_dir = (
        args.output_dir.resolve()
        if args.output_dir
        else (workspace / ".cursor" / "audit-results" / "general" / "audits")
    )

    metrics = FileMetricsAnalyzer(root).analyze()
    oversized = _extract_oversized_rows(metrics, max_file_lines=max_file_lines)

    paths = _write_artifacts(
        workspace=workspace,
        output_dir=output_dir,
        generated=generated,
        root=root,
        threshold_config_path=(args.config.resolve() if args.config else None),
        max_file_lines=max_file_lines,
        top=int(args.top),
        include_suggestions=not bool(args.no_suggestions),
        metrics=metrics,
        oversized=oversized,
        write_json=bool(args.json),
    )

    print(f"✅ [OK] Wrote {paths['md_path']}")
    if "json_path" in paths:
        print(f"✅ [OK] Wrote {paths['json_path']}")
    print(f"[SUMMARY] oversized={paths['oversized_count']} max_file_lines={paths['max_file_lines']}")

    exit_code = 0
    if args.fail_on_oversized:
        max_o = max(0, int(args.max_oversized))
        if int(paths.get("oversized_count", 0)) > max_o:
            print(
                f"❌ [FAIL] oversized_count={paths['oversized_count']} exceeds --max-oversized={max_o}",
                file=sys.stderr,
            )
            exit_code = 1
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())

