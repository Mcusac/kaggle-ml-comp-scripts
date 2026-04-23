#!/usr/bin/env python3
"""
Compute a consolidated numeric architecture score from existing artifacts.

Usage (cwd ``kaggle-ml-comp-scripts/scripts/``)::
  python -m layers.layer_2_devtools.level_1_impl.level_2.report_score --health-report path/to/health.json
  python -m layers.layer_2_devtools.level_1_impl.level_2.report_score --manifest path/to/manifest.json
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from datetime import date
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_SCRIPTS_ROOT = _SCRIPT_DIR.parents[3]
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import (
    parse_generated_optional,
)
from layers.layer_2_devtools.level_0_infra.level_0.path.audit_paths import (
    architecture_score_json_path,
)
from layers.layer_2_devtools.level_0_infra.level_0.path.workspace import resolve_workspace_root
from layers.layer_2_devtools.level_1_impl.level_1.api_health import (
    emit_health_report_view_api,
)


def _win_utf8_stdio() -> None:
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding="utf-8", errors="replace"
        )


def main() -> int:
    _win_utf8_stdio()
    parser = argparse.ArgumentParser(
        description="Compute a consolidated numeric architecture score.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--health-report", type=Path, help="Path to check_health JSON report")
    src.add_argument("--manifest", type=Path, help="Path to audit/pipeline manifest JSON")
    parser.add_argument(
        "--score-config",
        type=Path,
        default=None,
        help="Optional JSON config for scoring weights/penalties.",
    )
    parser.add_argument(
        "--scope",
        type=str,
        default="general",
        help="audit_results scope for output path when --write is used",
    )
    parser.add_argument(
        "--generated",
        type=str,
        default=None,
        help="YYYY-MM-DD to use in output filename (default: today)",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Also write score JSON under .cursor/audit-results/<scope>/summaries/",
    )
    args = parser.parse_args()

    g: date = parse_generated_optional(args.generated) or date.today()

    cfg: dict = {"view_kind": "score", "score_config_path": args.score_config}
    if args.health_report is not None:
        cfg["report_path"] = args.health_report
    if args.manifest is not None:
        cfg["manifest_path"] = args.manifest

    env = emit_health_report_view_api(cfg)
    if env["status"] != "ok":
        print("\n".join(env["errors"]), file=sys.stderr)
        return 1

    for line in env["data"]["lines"]:
        print(line)

    payload = env["data"]["score"]
    if args.write:
        workspace = resolve_workspace_root(Path.cwd())
        out = architecture_score_json_path(
            workspace, str(args.scope), g, stem="architecture_score"
        )
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"\n✅ Wrote {out}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

