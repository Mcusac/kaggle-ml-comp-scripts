"""
Orchestrate file-level suggestions into move waves (report-only).

This tool does NOT move files or rewrite imports. It converts the suggestion output
into an ordered checklist so you can apply changes in batches.
"""

from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path
from typing import Any

_SCRIPTS_ROOT = Path(__file__).resolve().parent.parent
if str(_SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_ROOT))

from layers.layer_2_devtools.level_1_impl.level_1.api_audit import (
    run_file_level_suggestions_with_artifacts,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    default_scripts_root = Path(__file__).resolve().parents[4]
    parser.add_argument(
        "--scripts-dir",
        type=Path,
        default=default_scripts_root,
        help="Scripts root directory containing `layers/` (default: scripts/).",
    )
    parser.add_argument(
        "--scope",
        type=str,
        default="general",
        choices=("general", "contests", "infra"),
        help="Which tiering scheme to apply.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Scope root that contains `level_N/` directories (defaults depend on --scope).",
    )
    parser.add_argument(
        "--contest-slug",
        type=str,
        default="level_csiro",
        help="Contest slug under level_1_impl/ when scope=contests (default: level_csiro).",
    )
    parser.add_argument(
        "--include",
        type=Path,
        action="append",
        default=[],
        help="Include only files under this path (repeatable).",
    )
    parser.add_argument(
        "--exclude",
        type=Path,
        action="append",
        default=[],
        help="Exclude files under this path (repeatable).",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Explicit output directory (default: workspace/.cursor/audit-results/<scope>/audits).",
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="YYYY-MM-DD for filename (default: today).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Also write JSON payload next to the markdown report.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with code 1 if any conflicts are detected.",
    )
    args = parser.parse_args()

    scripts_root = args.scripts_dir.resolve()
    generated = date.fromisoformat(args.date) if args.date else date.today()

    if args.root is not None:
        root = args.root.resolve()
    else:
        if args.scope == "general":
            root = (scripts_root / "layers" / "layer_0_core").resolve()
        elif args.scope == "infra":
            root = (
                scripts_root / "layers" / "layer_1_competition" / "level_0_infra"
            ).resolve()
        else:
            root = (
                scripts_root
                / "layers"
                / "layer_1_competition"
                / "level_1_impl"
                / args.contest_slug
            ).resolve()

    if args.scope == "general":
        import_prefixes = ["layers.layer_0_core."]
        policy = {"min_level_delta_for_outgoing": 1, "max_level_delta_for_incoming": -1}
    elif args.scope == "contests":
        import_prefixes = [f"layers.layer_1_competition.contests.{args.contest_slug}."]
        policy = {"min_level_delta_for_outgoing": 1, "max_level_delta_for_incoming": -1}
    else:
        import_prefixes = ["layers.layer_1_competition.level_0_infra."]
        policy = {"min_level_delta_for_outgoing": 0, "max_level_delta_for_incoming": 0}

    env = run_file_level_suggestions_with_artifacts(
        {
            "scripts_dir": scripts_root,
            "scope": args.scope,
            "root": root,
            "generated": generated,
            "include": [p.resolve() for p in args.include],
            "exclude": [p.resolve() for p in args.exclude],
            "write_json": bool(args.json),
            "output_dir": args.output_dir.resolve() if args.output_dir else None,
            "strict": bool(args.strict),
            "import_prefixes": import_prefixes,
            "policy": policy,
        }
    )
    if env["status"] != "ok":
        raise SystemExit("\n".join(env["errors"]))
    data = env["data"]
    payload = data["payload"]

    plan_md = _build_wave_plan_markdown(payload)
    md_path = Path(data["md_path"])
    wave_path = md_path.with_name(md_path.stem + "_waves.md")
    wave_path.write_text(plan_md, encoding="utf-8")
    print(f"[OK] Wrote {data['md_path']}")
    if "json_path" in data:
        print(f"[OK] Wrote {data['json_path']}")
    print(f"[OK] Wrote {wave_path}")
    print(data["summary_line"])
    code = int(data.get("exit_code", 0) or 0)
    if code:
        raise SystemExit(code)


def _build_wave_plan_markdown(payload: dict[str, Any]) -> str:
    rows = payload.get("rows", []) or []
    scope = str(payload.get("scope", ""))
    generated = str(payload.get("generated", ""))

    moves: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []

    for r in rows:
        if r.get("status") == "conflict":
            conflicts.append(r)
            continue
        if r.get("status") not in ("ok", "no_change"):
            continue
        cur = r.get("current_level")
        sug = r.get("suggested_level")
        if cur is None or sug is None:
            continue
        if int(sug) != int(cur):
            moves.append(r)

    by_target: dict[int, list[dict[str, Any]]] = {}
    for r in moves:
        tgt = int(r.get("suggested_level"))
        by_target.setdefault(tgt, []).append(r)

    lines: list[str] = [
        "---",
        f"generated: {generated}",
        "kind: file_level_suggestions_wave_plan",
        f"scope: {scope}",
        "---",
        "",
        "# File level suggestion wave plan (draft)",
        "",
        "This is a report-only checklist grouped by suggested target level.",
        "After each wave, apply moves/import rewrites/barrel regen, then rerun suggestions.",
        "",
    ]

    if conflicts:
        lines.append("## Conflicts (must resolve first)")
        lines.append("")
        for r in sorted(conflicts, key=lambda x: str(x.get("module", ""))):
            lines.append(f"- `{r.get('module', '')}` (lb={r.get('lb_required')}, ub={r.get('ub_allowed')})")
        lines.append("")

    if not by_target:
        lines.append("## Waves")
        lines.append("")
        lines.append("_No moves suggested._")
        lines.append("")
        return "\n".join(lines).rstrip("\n") + "\n"

    lines.append("## Waves")
    lines.append("")
    for tgt in sorted(by_target.keys()):
        lines.append(f"### Wave: move to level_{tgt}")
        lines.append("")
        for r in sorted(by_target[tgt], key=lambda x: str(x.get("module", ""))):
            lines.append(
                f"- [ ] `{r.get('module', '')}`: level_{r.get('current_level')} -> level_{r.get('suggested_level')}"
            )
        lines.append("")

    return "\n".join(lines).rstrip("\n") + "\n"


if __name__ == "__main__":
    main()

