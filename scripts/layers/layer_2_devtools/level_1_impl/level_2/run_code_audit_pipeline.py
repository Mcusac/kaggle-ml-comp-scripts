#!/usr/bin/env python3
"""Machine runner: audit target queue, per-target precheck, stack scans, manifest JSON.

Run from ``kaggle-ml-comp-scripts/scripts/``::

  python -m layers.layer_2_devtools.level_1_impl.level_2.run_code_audit_pipeline

Exit codes:
  0 — All enabled steps completed (envelope ``status == ok`` for the pipeline API).
  1 — Discovery failed, manifest write failed, or any enabled step reported an error
      (see ``aggregate.failed_steps`` in the manifest).
"""

import argparse
import io
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_SCRIPTS_ROOT = _SCRIPT_DIR.parents[3]
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_2.pipeline_ops import run_code_audit_pipeline


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
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=None,
        help="artifact_base (overrides discovery; must contain .cursor/audit-results)",
    )
    parser.add_argument(
        "--layers-root",
        type=Path,
        default=None,
        help="Override scripts/layers (default: <scripts>/layers)",
    )
    parser.add_argument(
        "--run-id",
        type=str,
        default=None,
        help="Run id (default: UTC YYYY-MM-DDTHHMMSSZ for default output directory)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Directory for manifest.json and audit_queue.json",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=None,
        help="Exact manifest file path (queue JSON written as sibling audit_queue.json)",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="YYYY-MM-DD for precheck/scan file stems (default: today)",
    )
    parser.add_argument(
        "--no-precheck",
        action="store_true",
        help="Skip per-target precheck",
    )
    parser.add_argument(
        "--no-general-scan",
        action="store_true",
        help="Skip general stack violation scan",
    )
    parser.add_argument(
        "--no-csiro-scan",
        action="store_true",
        help="Skip CSIRO contest tier scan",
    )
    parser.add_argument(
        "--no-oversized-scan",
        action="store_true",
        help="Skip oversized module scan",
    )
    parser.add_argument(
        "--run-package-boundary",
        action="store_true",
        help="Also run package boundary validation (default: off).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Forward strict mode to precheck (and contract validation when applicable)",
    )
    parser.add_argument(
        "--fail-on-skipped",
        action="store_true",
        help="Fail if any enabled pipeline step ends with status skipped (e.g. missing CSIRO root)",
    )
    parser.add_argument(
        "--max-targets",
        type=int,
        default=None,
        help="Cap number of precheck targets (testing/CI)",
    )
    parser.add_argument(
        "--no-queue-file",
        action="store_true",
        help="Do not write audit_queue.json (manifest still records queue summary)",
    )
    args = parser.parse_args()

    cfg: dict = {
        "scripts_root": _SCRIPTS_ROOT,
        "run_precheck": not args.no_precheck,
        "run_general_stack_scan": not args.no_general_scan,
        "run_csiro_scan": not args.no_csiro_scan,
        "run_oversized_module_scan": not args.no_oversized_scan,
        "run_package_boundary_validation": bool(args.run_package_boundary),
        "precheck_strict": bool(args.strict),
        "max_targets": args.max_targets,
        "write_queue_json": not args.no_queue_file,
        "fail_on_skipped": bool(args.fail_on_skipped),
    }
    if args.run_id:
        cfg["run_id"] = str(args.run_id)
    if args.date:
        cfg["generated"] = args.date
    if args.workspace_root:
        cfg["workspace_root"] = args.workspace_root
    if args.layers_root:
        cfg["layers_root"] = args.layers_root
    if args.manifest and args.output_dir:
        print("Use only one of --manifest and --output-dir", file=sys.stderr)
        return 1
    if args.manifest:
        cfg["manifest_path"] = args.manifest
    if args.output_dir:
        cfg["output_dir"] = args.output_dir

    env = run_code_audit_pipeline(cfg)
    if env["status"] != "ok":
        print("\n".join(env["errors"]), file=sys.stderr)
        return 1
    data = env["data"]
    print(f"✅ manifest: {data['manifest_path']}")
    if data.get("queue_path"):
        print(f"✅ queue:   {data['queue_path']}")
    code = int(data.get("overall_exit_code", 0))
    if code != 0:
        print(
            f"❌ overall_exit_code={code} failed_steps="
            f"{data['manifest']['aggregate']['failed_steps']}",
            file=sys.stderr,
        )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
