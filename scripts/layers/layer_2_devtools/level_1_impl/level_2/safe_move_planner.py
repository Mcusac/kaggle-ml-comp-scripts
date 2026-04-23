"""
Safe Move Planner.

Safely moves a module/file within a chosen root tree:
- compute destination path
- move file (dry-run default)
- rewrite imports referencing the moved module (drift-safe)
- optionally regenerate __init__.py barrels
- optionally verify imports
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_0_infra.level_0.fix import (
    MoveImportRewrite,
    build_move_import_rewrite_ops,
)
from layers.layer_2_devtools.level_0_infra.level_0.fix.import_rewrite_engine import (
    apply_edit_operations,
)
from layers.layer_2_devtools.level_0_infra.level_0.moves import (
    MovePlanError,
    MoveSpec,
    compute_move_plan,
)
from layers.layer_2_devtools.level_0_infra.level_0.path.workspace import resolve_workspace_root
from layers.layer_2_devtools.level_1_impl.level_1.api_maintenance import (
    run_verify_imports_cli_api,
)
from layers.layer_2_devtools.level_1_impl.level_2.regenerate_package_inits import (
    apply_regeneration,
)


@dataclass(frozen=True)
class _RunResult:
    md_path: Path
    json_path: Path | None


def _win_utf8_stdio() -> None:
    if sys.platform == "win32":
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def main() -> int:
    _win_utf8_stdio()

    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    single = sub.add_parser("single", help="Move one file/module.")
    _add_common_args(single)
    single.add_argument("--src", type=Path, default=None, help="Source file path under --root.")
    single.add_argument(
        "--src-module",
        type=str,
        default=None,
        help="Source module path relative to --root (e.g. level_3.foo.bar).",
    )
    single.add_argument(
        "--dest-level",
        type=int,
        default=None,
        help="Destination level_N (compute destination path by replacing level segment).",
    )
    single.add_argument(
        "--dest-path",
        type=Path,
        default=None,
        help="Explicit destination path under --root.",
    )

    batch = sub.add_parser("batch", help="Apply a batch of moves from a JSON file.")
    _add_common_args(batch)
    batch.add_argument(
        "--moves-json",
        type=Path,
        required=True,
        help="Moves JSON: [{src_module|src_path, dest_level|dest_path}, ...]",
    )

    conv = sub.add_parser("convert", help="Convert scan JSON into Safe Move Planner moves JSON.")
    conv.add_argument(
        "--scan-json",
        type=Path,
        required=True,
        help="Input scan JSON (level_violations_scan_*.json or file_level_suggestions_*.json).",
    )
    conv.add_argument(
        "--output",
        type=Path,
        required=True,
        help="Output moves JSON path.",
    )

    args = parser.parse_args()
    if args.cmd == "convert":
        return _run_convert(args)
    if args.cmd == "single":
        return _run_single(args)
    if args.cmd == "batch":
        return _run_batch(args)
    raise SystemExit(f"Unknown command: {args.cmd}")


def _add_common_args(p: argparse.ArgumentParser) -> None:
    p.add_argument(
        "--root",
        type=Path,
        required=True,
        help="Root directory containing level_N/ directories (scoped move tree).",
    )
    p.add_argument("--apply", action="store_true", help="Apply move and rewrites.")
    p.add_argument(
        "--include-tests",
        action="store_true",
        help="Include files matching test_*.py during rewrite scan.",
    )
    p.add_argument(
        "--max-changes-per-file",
        type=int,
        default=25,
        help="Safety cap on number of edits per file (default: 25).",
    )
    p.add_argument(
        "--regen-inits",
        choices=("off", "dry-run", "fix"),
        default="off",
        help="Regenerate __init__.py files for affected level trees.",
    )
    p.add_argument(
        "--verify",
        action="store_true",
        help="After apply, run verify_imports on --root to report remaining violations.",
    )
    p.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Write report here (default: <workspace>/.cursor/audit-results/general/audits).",
    )
    p.add_argument(
        "--date",
        type=str,
        default=None,
        help="YYYY-MM-DD for report filenames (default: today).",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Also write JSON payload next to markdown.",
    )


def _run_single(args: Any) -> int:
    root = Path(args.root).resolve()
    generated = date.fromisoformat(args.date) if args.date else date.today()

    try:
        plan = compute_move_plan(
            spec=MoveSpec(
                root=root,
                src_path=Path(args.src).resolve() if args.src else None,
                src_module=str(args.src_module) if args.src_module else None,
                dest_level=args.dest_level,
                dest_path=Path(args.dest_path).resolve() if args.dest_path else None,
            )
        )
    except MovePlanError as exc:
        print(f"❌ {exc}", file=sys.stderr)
        return 2

    run = _execute_move(
        root=root,
        generated=generated,
        plan=plan,
        apply=bool(args.apply),
        include_tests=bool(args.include_tests),
        max_changes_per_file=int(args.max_changes_per_file),
        regen_inits=str(args.regen_inits),
        verify=bool(args.verify),
        output_dir=Path(args.output_dir).resolve() if args.output_dir else None,
        write_json=bool(args.json),
        batch=None,
    )
    _print_paths(run)
    return 0


def _run_batch(args: Any) -> int:
    root = Path(args.root).resolve()
    generated = date.fromisoformat(args.date) if args.date else date.today()

    moves = _load_moves_json(Path(args.moves_json))
    if not moves:
        print(f"❌ No moves found in {Path(args.moves_json).as_posix()}", file=sys.stderr)
        return 2

    batch_rows: list[dict[str, Any]] = []
    for idx, m in enumerate(moves, start=1):
        try:
            spec = MoveSpec(
                root=root,
                src_path=Path(m["src_path"]).resolve() if m.get("src_path") else None,
                src_module=str(m["src_module"]) if m.get("src_module") else None,
                dest_level=int(m["dest_level"]) if m.get("dest_level") is not None else None,
                dest_path=Path(m["dest_path"]).resolve() if m.get("dest_path") else None,
            )
            plan = compute_move_plan(spec=spec)
        except (KeyError, TypeError, ValueError, MovePlanError) as exc:
            print(f"❌ move[{idx}] invalid: {exc}", file=sys.stderr)
            return 2
        batch_rows.append(
            {
                "idx": idx,
                "src_module": plan.old_module,
                "dest_module": plan.new_module,
                "src_path": plan.src_path.as_posix(),
                "dest_path": plan.dest_path.as_posix(),
            }
        )

    run = _execute_batch(
        root=root,
        generated=generated,
        batch_rows=batch_rows,
        apply=bool(args.apply),
        include_tests=bool(args.include_tests),
        max_changes_per_file=int(args.max_changes_per_file),
        regen_inits=str(args.regen_inits),
        verify=bool(args.verify),
        output_dir=Path(args.output_dir).resolve() if args.output_dir else None,
        write_json=bool(args.json),
    )
    _print_paths(run)
    return 0


def _execute_batch(
    *,
    root: Path,
    generated: date,
    batch_rows: list[dict[str, Any]],
    apply: bool,
    include_tests: bool,
    max_changes_per_file: int,
    regen_inits: str,
    verify: bool,
    output_dir: Path | None,
    write_json: bool,
) -> _RunResult:
    workspace = resolve_workspace_root(root)
    out_dir = (
        output_dir.resolve()
        if output_dir
        else (workspace / ".cursor" / "audit-results" / "general" / "audits")
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / f"safe_move_planner_batch_{generated.isoformat()}.md"
    json_path = out_dir / f"safe_move_planner_batch_{generated.isoformat()}.json" if write_json else None

    results: list[dict[str, Any]] = []
    for row in batch_rows:
        spec = MoveSpec(
            root=root,
            src_module=str(row["src_module"]),
            dest_path=Path(row["dest_path"]).resolve(),
        )
        plan = compute_move_plan(spec=spec)
        payload = _execute_move_payload(
            root=root,
            generated=generated,
            plan=plan,
            apply=apply,
            include_tests=include_tests,
            max_changes_per_file=max_changes_per_file,
            regen_inits=regen_inits,
            verify=verify,
            output_dir=out_dir,
            write_json=False,
        )
        results.append(payload)

    batch_payload: dict[str, Any] = {
        "schema": "safe_move_planner_batch_run.v1",
        "generated": generated.isoformat(),
        "root": root.as_posix(),
        "apply": bool(apply),
        "moves": batch_rows,
        "runs": results,
    }
    md_path.write_text(_render_batch_markdown(batch_payload), encoding="utf-8")
    if json_path is not None:
        json_path.write_text(json.dumps(batch_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return _RunResult(md_path=md_path, json_path=json_path)


def _execute_move(
    *,
    root: Path,
    generated: date,
    plan: Any,
    apply: bool,
    include_tests: bool,
    max_changes_per_file: int,
    regen_inits: str,
    verify: bool,
    output_dir: Path | None,
    write_json: bool,
    batch: dict[str, Any] | None,
) -> _RunResult:
    workspace = resolve_workspace_root(root)
    out_dir = (
        output_dir.resolve()
        if output_dir
        else (workspace / ".cursor" / "audit-results" / "general" / "audits")
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    md_path = out_dir / f"safe_move_planner_{generated.isoformat()}.md"
    json_path = out_dir / f"safe_move_planner_{generated.isoformat()}.json" if write_json else None

    payload = _execute_move_payload(
        root=root,
        generated=generated,
        plan=plan,
        apply=apply,
        include_tests=include_tests,
        max_changes_per_file=max_changes_per_file,
        regen_inits=regen_inits,
        verify=verify,
        output_dir=out_dir,
        write_json=write_json,
    )
    if batch is not None:
        payload["batch"] = batch

    md_path.write_text(_render_markdown(payload), encoding="utf-8")
    if json_path is not None:
        json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return _RunResult(md_path=md_path, json_path=json_path)


def _execute_move_payload(
    *,
    root: Path,
    generated: date,
    plan: Any,
    apply: bool,
    include_tests: bool,
    max_changes_per_file: int,
    regen_inits: str,
    verify: bool,
    output_dir: Path,
    write_json: bool,
) -> dict[str, Any]:
    move_actions: list[str] = []
    if plan.dest_path.parent != plan.src_path.parent:
        move_actions.append(f"mkdir -p {plan.dest_path.parent.as_posix()}")
    move_actions.append(f"move {plan.src_path.as_posix()} -> {plan.dest_path.as_posix()}")

    move_applied = False
    if apply:
        plan.dest_path.parent.mkdir(parents=True, exist_ok=True)
        plan.src_path.rename(plan.dest_path)
        move_applied = True

    ops, warnings = build_move_import_rewrite_ops(
        root=root,
        rewrite=MoveImportRewrite(old_module=plan.old_module, new_module=plan.new_module),
        include_tests=bool(include_tests),
    )
    results, summary, apply_errors = apply_edit_operations(
        ops,
        apply=bool(apply),
        max_changes_per_file=max(0, int(max_changes_per_file)),
    )
    warnings.extend(apply_errors)
    changed_files = sorted(
        {r.path.as_posix() for r in results if int(getattr(r, "edits_applied", 0) or 0) > 0}
    )

    regen_summary: dict[str, Any] | None = None
    if regen_inits != "off":
        targets = _compute_regen_targets(root=root, moved_src=plan.src_path, moved_dest=plan.dest_path)
        drifts: list[dict[str, Any]] = []
        rc_total = 0
        for t in targets:
            rc, drift_objs = apply_regeneration(
                t,
                include_tests=bool(include_tests),
                dry_run=(regen_inits == "dry-run" or not apply),
            )
            rc_total = max(rc_total, int(rc))
            for d in drift_objs:
                drifts.append({"init_path": str(d.init_path)})
        regen_summary = {
            "targets": [p.as_posix() for p in targets],
            "exit_code": int(rc_total),
            "drifts": drifts,
        }

    verify_summary: dict[str, Any] | None = None
    if verify and apply:
        env = run_verify_imports_cli_api(
            {
                "scripts_root": (Path(__file__).resolve().parents[4]),
                "root": root,
                "include_tests": bool(include_tests),
                "write_json": False,
                "output_dir": output_dir,
                "generated": generated,
            }
        )
        if env["status"] != "ok":
            verify_summary = {"status": "error", "errors": env.get("errors", [])}
        else:
            data = env["data"]
            verify_summary = {
                "status": "ok",
                "md_path": data.get("md_path"),
                "violation_count": int(data.get("violation_count", 0) or 0),
                "parse_error_count": int(data.get("parse_error_count", 0) or 0),
            }

    payload: dict[str, Any] = {
        "schema": "safe_move_planner_run.v1",
        "generated": generated.isoformat(),
        "root": root.as_posix(),
        "apply": bool(apply),
        "move": {
            "src_path": plan.src_path.as_posix(),
            "dest_path": plan.dest_path.as_posix(),
            "old_module": plan.old_module,
            "new_module": plan.new_module,
            "actions": move_actions,
            "applied": bool(move_applied),
        },
        "rewrite": {
            "files_considered": int(summary.files_considered),
            "files_changed": int(summary.files_changed),
            "edits_applied": int(summary.edits_applied),
            "changed_files": changed_files,
            "warnings": warnings,
        },
        "regen_inits": regen_summary,
        "verify_imports": verify_summary,
    }
    return payload


def _load_moves_json(path: Path) -> list[dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"❌ Failed to read moves JSON: {path.as_posix()}\n{exc}")
    if not isinstance(data, list):
        raise SystemExit("❌ Moves JSON must be a list.")
    out: list[dict[str, Any]] = []
    for row in data:
        if isinstance(row, dict):
            out.append(row)
    return out


def _run_convert(args: Any) -> int:
    scan = Path(args.scan_json)
    out = Path(args.output)
    try:
        data = json.loads(scan.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"❌ Failed to read scan JSON: {scan.as_posix()}\n{exc}", file=sys.stderr)
        return 2

    moves = _convert_scan_payload_to_moves(data)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(moves, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"✅ [OK] Wrote {out}")
    return 0


def _convert_scan_payload_to_moves(scan_json: dict[str, Any]) -> list[dict[str, Any]]:
    # level_violations_scan_*.json produced by scan_level_violations
    if isinstance(scan_json.get("violations"), list):
        moves: list[dict[str, Any]] = []
        seen: set[tuple[str, int]] = set()
        for v in scan_json.get("violations", []) or []:
            if not isinstance(v, dict):
                continue
            src = v.get("file")
            lvl = v.get("suggested_min_level")
            if not isinstance(src, str) or lvl is None:
                continue
            try:
                dest_level = int(lvl)
            except (TypeError, ValueError):
                continue
            key = (src, dest_level)
            if key in seen:
                continue
            seen.add(key)
            moves.append({"src_module": src, "dest_level": dest_level})
        return moves

    # file_level_suggestions_*.json payload
    payload = scan_json.get("payload")
    if isinstance(payload, dict) and isinstance(payload.get("rows"), list):
        moves2: list[dict[str, Any]] = []
        for r in payload.get("rows", []) or []:
            if not isinstance(r, dict):
                continue
            if r.get("status") not in ("ok", "no_change"):
                continue
            mod = r.get("module")
            cur = r.get("current_level")
            sug = r.get("suggested_level")
            if not isinstance(mod, str) or cur is None or sug is None:
                continue
            try:
                cur_i = int(cur)
                sug_i = int(sug)
            except (TypeError, ValueError):
                continue
            if sug_i == cur_i:
                continue
            moves2.append({"src_module": mod, "dest_level": sug_i})
        return moves2

    raise SystemExit("❌ Unrecognized scan JSON shape for conversion.")


def _print_paths(run: _RunResult) -> None:
    print(f"✅ [OK] Wrote {run.md_path}")
    if run.json_path is not None:
        print(f"✅ [OK] Wrote {run.json_path}")


def _compute_regen_targets(*, root: Path, moved_src: Path, moved_dest: Path) -> list[Path]:
    targets: set[Path] = set()
    for p in (moved_src, moved_dest):
        try:
            rel = p.resolve().relative_to(root.resolve())
        except ValueError:
            continue
        parts = list(rel.parts)
        for i, part in enumerate(parts):
            if part.startswith("level_") and part[6:].isdigit():
                targets.add((root / Path(*parts[: i + 1])).resolve())
                break
    return sorted(targets, key=lambda x: x.as_posix())


def _render_markdown(payload: dict[str, Any]) -> str:
    mv = payload.get("move", {})
    rw = payload.get("rewrite", {})
    regen = payload.get("regen_inits")
    ver = payload.get("verify_imports")

    lines: list[str] = [
        "---",
        f"generated: {payload.get('generated', '')}",
        "artifact: safe_move_planner_run",
        "schema: safe_move_planner_run.v1",
        f"root: {payload.get('root', '')}",
        "---",
        "",
        "# Safe Move Planner",
        "",
        f"- Apply: `{payload.get('apply')}`",
        "",
        "## Move",
        "",
        f"- Source: `{mv.get('src_path', '')}`",
        f"- Destination: `{mv.get('dest_path', '')}`",
        f"- Module: `{mv.get('old_module', '')}` → `{mv.get('new_module', '')}`",
        "",
        "Planned actions:",
        "",
    ]
    for a in mv.get("actions", []) or []:
        lines.append(f"- {a}")
    lines.append("")

    lines.extend(
        [
            "## Import rewrites",
            "",
            f"- Files considered: {rw.get('files_considered', 0)}",
            f"- Files changed: {rw.get('files_changed', 0)}",
            f"- Edits applied: {rw.get('edits_applied', 0)}",
            "",
        ]
    )
    changed = rw.get("changed_files", []) or []
    if changed:
        lines.append("Changed files:")
        lines.append("")
        for p in changed:
            lines.append(f"- `{p}`")
        lines.append("")
    warns = rw.get("warnings", []) or []
    if warns:
        lines.append("Warnings/errors (first 50):")
        lines.append("")
        for w in warns[:50]:
            lines.append(f"- {w}")
        lines.append("")

    if regen is not None:
        lines.append("## Barrel regeneration (__init__.py)")
        lines.append("")
        lines.append(f"- Targets: {len(regen.get('targets', []) or [])}")
        for t in regen.get("targets", []) or []:
            lines.append(f"  - `{t}`")
        lines.append("")

    if ver is not None:
        lines.append("## Verification (verify_imports)")
        lines.append("")
        if ver.get("status") == "ok":
            lines.append(f"- Report: `{ver.get('md_path', '')}`")
            lines.append(f"- Violations: {ver.get('violation_count', 0)}")
            lines.append(f"- Parse errors: {ver.get('parse_error_count', 0)}")
        else:
            lines.append(f"- Status: `{ver.get('status')}`")
            for e in ver.get("errors", []) or []:
                lines.append(f"  - {e}")
        lines.append("")

    return "\n".join(lines).rstrip("\n") + "\n"


def _render_batch_markdown(payload: dict[str, Any]) -> str:
    runs = payload.get("runs", []) or []
    lines: list[str] = [
        "---",
        f"generated: {payload.get('generated', '')}",
        "artifact: safe_move_planner_batch_run",
        "schema: safe_move_planner_batch_run.v1",
        f"root: {payload.get('root', '')}",
        "---",
        "",
        "# Safe Move Planner (batch)",
        "",
        f"- Apply: `{payload.get('apply')}`",
        f"- Moves: {len(payload.get('moves', []) or [])}",
        "",
    ]
    for idx, run in enumerate(runs, start=1):
        mv = (run or {}).get("move", {}) if isinstance(run, dict) else {}
        lines.append(f"## Move {idx}")
        lines.append("")
        lines.append(f"- `{mv.get('old_module', '')}` → `{mv.get('new_module', '')}`")
        lines.append(f"- `{mv.get('src_path', '')}` → `{mv.get('dest_path', '')}`")
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


if __name__ == "__main__":
    raise SystemExit(main())

