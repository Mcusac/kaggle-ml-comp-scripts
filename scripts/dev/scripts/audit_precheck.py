#!/usr/bin/env python3
"""CLI entrypoint for audit precheck.

This wrapper intentionally avoids importing the devtools stack at module import
time so that missing optional dependencies (notably ``torchvision``) can be
handled gracefully.
"""

import argparse
from dataclasses import dataclass
from datetime import date as _date
import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from precheck_artifact_root import resolve_audit_artifact_root

_SCRIPTS_ROOT = Path(__file__).resolve().parents[2]
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

# Ensure top-level `level_0`… imports resolve (layer_0_core on sys.path).
try:
    import path_bootstrap

    path_bootstrap.prepend_framework_paths()
except Exception:
    # This script has a graceful fallback path below; keep bootstrap best-effort.
    pass


@dataclass(frozen=True)
class _FallbackArgs:
    audit_scope: str
    level_name: str
    level_path: Path | None
    workspace_root: Path | None
    generated: str | None


def _write_skipped_precheck(*, args: _FallbackArgs, reason: str) -> int:
    ws = (
        args.workspace_root.resolve()
        if args.workspace_root is not None
        else resolve_audit_artifact_root(args.level_path or _SCRIPTS_ROOT)
    )
    gen = args.generated or _date.today().isoformat()
    out_base = (
        ws
        / ".cursor"
        / "audit-results"
        / args.audit_scope
        / "summaries"
        / f"precheck_{args.level_name}_{gen}"
    )
    out_base.parent.mkdir(parents=True, exist_ok=True)

    md = "\n".join(
        [
            "---",
            f"generated: {gen}",
            f"audit_scope: {args.audit_scope}",
            f"level_name: {args.level_name}",
            "artifact_kind: precheck",
            "precheck_status: skipped_machine_script",
            "---",
            "",
            "# Precheck (machine script unavailable)",
            "",
            "## Why skipped",
            "",
            reason.rstrip(),
            "",
            "## Next steps",
            "",
            "- Install/enable optional dependencies (notably `torchvision`) in your local venv, then rerun this command to get machine-backed Phase 7 reconciliation.",
            "",
        ]
    ).rstrip() + "\n"

    payload = {
        "generated": gen,
        "audit_scope": args.audit_scope,
        "level_name": args.level_name,
        "artifact_kind": "precheck",
        "precheck_status": "skipped_machine_script",
        "reason": reason,
    }

    Path(str(out_base) + ".md").write_text(md, encoding="utf-8")
    Path(str(out_base) + ".json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    # Avoid unicode output issues on Windows consoles with legacy encodings.
    print(f"[WARN] audit_precheck skipped: {reason}")
    print(f"[OK] Wrote {Path(str(out_base) + '.md')}")
    print(f"[OK] Wrote {Path(str(out_base) + '.json')}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="audit_precheck wrapper")
    parser.add_argument(
        "--audit-scope",
        choices=("general", "competition_infra", "contests_special"),
        required=True,
    )
    parser.add_argument(
        "--level-path",
        type=Path,
        help="Directory (or file) under the audited level package",
    )
    parser.add_argument(
        "--level-name",
        type=str,
        required=True,
        help="Artifact key, e.g. level_3, level_csiro_level_1",
    )
    parser.add_argument(
        "--workspace-root",
        type=Path,
        default=None,
        help=(
            "artifact_base: directory with .cursor/audit-results (default: discover; "
            "prefers input/kaggle-ml-comp-scripts when under that package)"
        ),
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="YYYY-MM-DD for filename (default: today)",
    )
    parser.add_argument(
        "--full-general-scan",
        action="store_true",
        help="general scope only: scan all layer_0..10 under default layer_0_core",
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Write only JSON (no markdown)",
    )
    parser.add_argument(
        "--precheck-kind",
        choices=("auto", "contest_tier", "contest_root", "special_tree"),
        default="auto",
    )
    args = parser.parse_args()

    try:
        from layers.layer_2_devtools.level_1_impl.level_2.audit_precheck import (  # type: ignore
            main as _devtools_main,
        )
    except ModuleNotFoundError as exc:
        fb = _FallbackArgs(
            audit_scope=args.audit_scope,
            level_name=args.level_name,
            level_path=args.level_path,
            workspace_root=args.workspace_root,
            generated=args.date,
        )
        return _write_skipped_precheck(args=fb, reason=f"ModuleNotFoundError: {exc}")

    # Hand off to the real CLI (which now also degrades gracefully once imported).
    return int(_devtools_main())


if __name__ == "__main__":
    raise SystemExit(main())
