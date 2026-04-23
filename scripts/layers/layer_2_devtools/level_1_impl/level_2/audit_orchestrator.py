#!/usr/bin/env python3
"""Audit Orchestrator (devtool): runs the full 8.1 checklist and writes manifest v2.

Run from ``kaggle-ml-comp-scripts/scripts/``::

  python -m layers.layer_2_devtools.level_1_impl.level_2.audit_orchestrator
"""

import argparse
import io
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_SCRIPTS_ROOT = _SCRIPT_DIR.parents[3]
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_2.audit_orchestrator_ops import (  # noqa: E402
    run_audit_orchestrator,
)


def _win_utf8_stdio() -> None:
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


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
        help="YYYY-MM-DD for report file stems (default: today)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Forward strict mode to precheck (contract validation) when applicable",
    )
    parser.add_argument(
        "--fail-on-skipped",
        action="store_true",
        help="Fail if any enabled step ends with status skipped",
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

    parser.add_argument("--no-precheck", action="store_true", help="Skip per-target precheck")
    parser.add_argument(
        "--no-dependency-validation",
        action="store_true",
        help="Skip layered dependency validation step",
    )
    parser.add_argument(
        "--no-import-validation",
        action="store_true",
        help="Skip import validation (verify_imports) step",
    )
    parser.add_argument(
        "--no-circular-deps",
        action="store_true",
        help="Skip circular dependency scan step",
    )
    parser.add_argument(
        "--no-barrel-enforcement",
        action="store_true",
        help="Skip barrel enforcement scan step",
    )
    parser.add_argument(
        "--no-dead-symbols",
        action="store_true",
        help="Skip dead symbol detector step",
    )

    args = parser.parse_args()

    cfg: dict = {
        "scripts_root": _SCRIPTS_ROOT,
        "run_precheck": not args.no_precheck,
        "run_dependency_validation": not args.no_dependency_validation,
        "run_import_validation": not args.no_import_validation,
        "run_circular_deps": not args.no_circular_deps,
        "run_barrel_enforcement": not args.no_barrel_enforcement,
        "run_dead_symbols": not args.no_dead_symbols,
        "precheck_strict": bool(args.strict),
        "max_targets": args.max_targets,
        "write_queue_json": not args.no_queue_file,
        "fail_on_skipped": bool(args.fail_on_skipped),
    }
    if args.run_id:
        cfg["run_id"] = str(args.run_id)
    if args.date:
        cfg["generated"] = str(args.date)
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

    env = run_audit_orchestrator(cfg)
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
            f"❌ overall_exit_code={code} failed_steps={data['manifest']['aggregate']['failed_steps']}",
            file=sys.stderr,
        )
    return code


if __name__ == "__main__":
    raise SystemExit(main())

