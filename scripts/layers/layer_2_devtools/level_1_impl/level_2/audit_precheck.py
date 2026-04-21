#!/usr/bin/env python3
"""
Run static import/layering precheck for one audit target; write markdown + JSON
under .cursor/audit-results/<scope>/summaries/.

Run from ``kaggle-ml-comp-scripts/scripts/``::

  python -m layers.layer_2_devtools.level_1_impl.level_2.audit_precheck

Does not replace the planner/auditor; feeds machine findings for Phase 7 reconciliation.
"""

import argparse
from dataclasses import dataclass
from datetime import date as _date
import io
import json
import os
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_SCRIPTS_ROOT = _SCRIPT_DIR.parents[3]
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

try:
    import path_bootstrap

    path_bootstrap.prepend_framework_paths()
except Exception:
    pass

from layers.layer_2_devtools.level_1_impl.level_2.audit_artifact_bootstrap import (
    get_resolve_audit_artifact_root,
)


@dataclass(frozen=True)
class _FallbackArgs:
    audit_scope: str
    level_name: str
    level_path: Path | None
    workspace_root: Path | None
    generated: str | None


def _strict_from_env_and_flag(strict_flag: bool) -> bool:
    if strict_flag:
        return True
    v = os.environ.get("AUDIT_MACHINE_STRICT", "").strip().lower()
    return v in ("1", "true", "yes", "on")


def _write_skipped_precheck(*, args: _FallbackArgs, reason: str, strict: bool) -> int:
    ws = (
        args.workspace_root.resolve()
        if args.workspace_root is not None
        else get_resolve_audit_artifact_root()(args.level_path or _SCRIPTS_ROOT)
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
            "## What this means",
            "",
            "- This environment could not import the devtools precheck stack.",
            "- The code-audit orchestrator can still run (inventories/audits); Phase 7 machine reconciliation is unavailable.",
            "",
            "## How to get machine precheck locally",
            "",
            "- Create/activate a venv where optional deps (notably `torchvision`) import cleanly, then rerun this command.",
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
    if strict:
        print(
            "[FAIL] Strict mode: precheck_status is skipped_machine_script — "
            "exit 1 (install optional deps or omit --strict / AUDIT_MACHINE_STRICT)",
            file=sys.stderr,
        )
        return 1
    return 0


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
        help=(
            "contests_special only: auto infers from path/name, or force tier / "
            "contest package root / layer_Z-style tree"
        ),
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help=(
            "Non-zero exit if the machine precheck stack cannot run (skip stub). "
            "Also enabled when env AUDIT_MACHINE_STRICT is 1/true/yes/on (CI)."
        ),
    )
    args = parser.parse_args()
    strict = _strict_from_env_and_flag(bool(args.strict))
    try:
        from layers.layer_2_devtools.level_1_impl.level_1.api_audit import (  # type: ignore
            run_audit_precheck_cli_complete,
        )
    except ModuleNotFoundError as exc:
        fb = _FallbackArgs(
            audit_scope=args.audit_scope,
            level_name=args.level_name,
            level_path=args.level_path,
            workspace_root=args.workspace_root,
            generated=args.date,
        )
        missing = str(exc)
        return _write_skipped_precheck(
            args=fb, reason=f"ModuleNotFoundError: {missing}", strict=strict
        )

    env = run_audit_precheck_cli_complete(
        {
            "scripts_root": _SCRIPTS_ROOT,
            "audit_scope": args.audit_scope,
            "level_name": args.level_name,
            "level_path": args.level_path,
            "workspace_root": args.workspace_root,
            "generated": args.date,
            "json_only": args.json_only,
            "full_general_scan": args.full_general_scan,
            "precheck_kind": args.precheck_kind,
            "strict": strict,
        }
    )
    if env["status"] != "ok":
        raise SystemExit("\n".join(env["errors"]))
    for msg in env["data"]["messages"]:
        print(msg)
    return int(env["data"]["exit_code"])


if __name__ == "__main__":
    raise SystemExit(main())
