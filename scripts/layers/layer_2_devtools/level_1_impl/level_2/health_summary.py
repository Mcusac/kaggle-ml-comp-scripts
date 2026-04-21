#!/usr/bin/env python3
"""
Run a comprehensive code health analysis and summarize key findings.

Typical usage (cwd ``kaggle-ml-comp-scripts/scripts/``)::
    python -m layers.layer_2_devtools.level_1_impl.level_2.health_summary --root .
"""

import argparse
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_SCRIPTS_ROOT = _SCRIPT_DIR.parents[3]
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_1.api_health import run_health_summary_api


def main() -> int:
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(
            sys.stdout.buffer, encoding="utf-8", errors="replace"
        )
        sys.stderr = io.TextIOWrapper(
            sys.stderr.buffer, encoding="utf-8", errors="replace"
        )

    parser = argparse.ArgumentParser(
        description="Run comprehensive health analysis and summaries.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent.parent,
        help="Root directory to analyze (passed to health analyzers as --root).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("output/health/health_report.json"),
        help="Path to write JSON health report.",
    )
    parser.add_argument(
        "--previous",
        type=Path,
        help="Optional previous JSON report for before/after comparison.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Optional threshold configuration file (JSON); affects duplication min_lines.",
    )
    parser.add_argument(
        "--skip-duplication",
        action="store_true",
        help="Skip duplication detection.",
    )
    parser.add_argument(
        "--skip-solid",
        action="store_true",
        help="Skip SOLID checks.",
    )
    parser.add_argument(
        "--skip-dead-code",
        action="store_true",
        help="Skip dead code detection.",
    )

    args = parser.parse_args()

    env = run_health_summary_api(
        {
            "root": args.root,
            "output_json": args.output.resolve(),
            "previous": args.previous,
            "threshold_config_path": args.config,
            "skip_duplication": args.skip_duplication,
            "skip_solid": args.skip_solid,
            "skip_dead_code": args.skip_dead_code,
        }
    )
    if env["status"] != "ok":
        print(f"❌ Error: {'; '.join(env['errors'])}")
        return 1
    rc = env["data"]["exit_code"]
    if rc == 0:
        print("\n✅ Health summary completed successfully.")
    else:
        print(f"\n⚠️ Health summary completed with non-zero exit code: {rc}")
    return int(rc)


if __name__ == "__main__":
    raise SystemExit(main())
