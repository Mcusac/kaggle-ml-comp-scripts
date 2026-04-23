"""Code-fix machine pipeline (deterministic orchestration of existing fix tools).

This is the machine counterpart to the chat `/code-fix` flow: it composes existing
devtools APIs in a deterministic order and writes a single FIX_RUN summary artifact.

Design constraints:
- Tool-first: delegate all real edits to existing deterministic tools/APIs.
- Default dry-run: do not write unless `apply=True`.
- No tempfile usage: write only to deterministic final paths under `.cursor/audit-results/...`.
"""

from __future__ import annotations

import importlib.util
import re
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_1_impl.level_2.audit_artifact_bootstrap import (
    get_resolve_audit_artifact_root,
)

_ENVELOPE_MOD: Any = None
_API_MAINTENANCE_MOD: Any = None
_API_VIOLATIONS_MOD: Any = None


def _get_envelope() -> Any:
    global _ENVELOPE_MOD
    if _ENVELOPE_MOD is not None:
        return _ENVELOPE_MOD
    ep = (
        Path(__file__).resolve().parents[2]
        / "level_0_infra"
        / "level_0"
        / "contracts"
        / "envelope.py"
    )
    name = "devtools_envelope_fix_pipeline"
    spec = importlib.util.spec_from_file_location(name, ep)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load envelope from {ep}")
    mod: Any = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _ENVELOPE_MOD = mod
    return mod


_e = _get_envelope()
_err = _e.err
_ok = _e.ok
_parse_generated_optional = _e.parse_generated_optional


def _load_level1_api_module(filename: str, module_name: str) -> Any:
    path = Path(__file__).resolve().parent.parent / "level_1" / filename
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {filename} from {path}")
    mod: Any = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _get_api_maintenance() -> Any:
    global _API_MAINTENANCE_MOD
    if _API_MAINTENANCE_MOD is None:
        _API_MAINTENANCE_MOD = _load_level1_api_module(
            "api_maintenance.py", "devtools_level1_api_maintenance_fix_pipeline"
        )
    return _API_MAINTENANCE_MOD


def _get_api_violations() -> Any:
    global _API_VIOLATIONS_MOD
    if _API_VIOLATIONS_MOD is None:
        _API_VIOLATIONS_MOD = _load_level1_api_module(
            "api_violations.py", "devtools_level1_api_violations_fix_pipeline"
        )
    return _API_VIOLATIONS_MOD


def _utc_now_iso() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _sanitize_slug(s: str) -> str:
    s2 = re.sub(r"[^A-Za-z0-9_]+", "_", s.strip())
    s2 = re.sub(r"_+", "_", s2).strip("_")
    return s2 or "target"


def _resolve_audit_scope(target_root: Path) -> str:
    p = target_root.as_posix().lower()
    if "/layer_0_core/" in p:
        return "general"
    if "/layer_1_competition/level_0_infra/" in p:
        return "competition_infra"
    if "/layer_1_competition/contests/" in p:
        return "contests_special"
    return "general"


def _derive_level_name(scripts_root: Path, target_root: Path, audit_scope: str) -> str:
    try:
        rel = target_root.resolve().relative_to((scripts_root / "layers").resolve())
    except ValueError:
        rel = target_root.resolve().name  # degraded
        return _sanitize_slug(str(rel))

    parts = rel.parts
    if audit_scope == "general":
        # scripts/layers/layer_0_core/level_N/...
        if len(parts) >= 2 and parts[0] == "layer_0_core":
            return _sanitize_slug(parts[1])
        return _sanitize_slug(parts[0])

    if audit_scope == "competition_infra":
        # scripts/layers/layer_1_competition/level_0_infra/level_N/...
        if len(parts) >= 3 and parts[0] == "layer_1_competition" and parts[1] == "level_0_infra":
            return _sanitize_slug(parts[2])
        return _sanitize_slug(parts[-1])

    if audit_scope == "contests_special":
        # scripts/layers/layer_1_competition/contests/<contest_pkg>/(level_K | root)
        if len(parts) >= 3 and parts[0] == "layer_1_competition" and parts[1] == "contests":
            contest_pkg = parts[2]
            if len(parts) >= 4 and re.fullmatch(r"level_\d+", parts[3]):
                k = parts[3].split("_", 1)[1]
                return _sanitize_slug(f"{contest_pkg}_level_{k}")
            return _sanitize_slug(f"{contest_pkg}_root")
        return _sanitize_slug(parts[-1])

    return _sanitize_slug(parts[-1])


def _write_fix_run(
    *,
    artifact_base: Path,
    audit_scope: str,
    level_slug: str,
    generated_date: date,
    body_lines: list[str],
) -> Path:
    out_dir = artifact_base / ".cursor" / "audit-results" / audit_scope / "summaries"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"FIX_RUN_{level_slug}_{generated_date.isoformat()}.md"
    out_path.write_text("\n".join(body_lines) + "\n", encoding="utf-8")
    return out_path


def run_code_fix_pipeline(config: dict[str, Any]) -> dict[str, Any]:
    """Run a deterministic fix pipeline on a target tree and emit a FIX_RUN summary.

    Config:
        - scripts_root (Path-like, required): `.../kaggle-ml-comp-scripts/scripts`
        - target_root (Path-like, required): tree under `scripts/layers/...`
        - generated (date or YYYY-MM-DD, optional): used for FIX_RUN filename (default today)
        - audit_scope (str, optional): override (`general` | `competition_infra` | `contests_special`)
        - level_name (str, optional): override slug base for FIX_RUN filename
        - apply (bool): default False (dry-run)
        - include_tests (bool): pass-through where supported; default False
        - tools (list[str]): requested tools in order. Supported:
            `apply_violation_fixes`, `fix_imports`, `cleanup_imports`,
            `organize_imports`, `init_regen`, `verify_imports`
        - audits_dir (Path-like, optional): folder containing `level_violations_scan_*.json`
        - scan_json (Path-like, optional): explicit scan JSON path for `apply_violation_fixes`
        - unused_imports_report (Path-like, optional): health report JSON for `cleanup_imports`
        - cleanup_no_organize_imports (bool): forwarded to cleanup tool (default False)
        - cleanup_format (bool), cleanup_format_tool (str), cleanup_format_args (list[str])
        - init_exclude_symbol (list[str]), init_include_symbol (list[str])
        - verify_write_json (bool): default False
    """
    try:
        scripts_root = Path(config["scripts_root"]).resolve()
        target_root = Path(config["target_root"]).resolve()
    except (KeyError, TypeError) as exc:
        return _err([f"scripts_root and target_root are required: {exc}"])

    raw_gen = config.get("generated")
    generated: date = _parse_generated_optional(raw_gen) or date.today()

    apply = bool(config.get("apply", False))
    include_tests = bool(config.get("include_tests", False))
    tools = list(config.get("tools") or [])
    if not tools:
        tools = [
            "apply_violation_fixes",
            "fix_imports",
            "cleanup_imports",
            "organize_imports",
            "init_regen",
            "verify_imports",
        ]

    audit_scope = str(config.get("audit_scope") or _resolve_audit_scope(target_root))
    if audit_scope not in ("general", "competition_infra", "contests_special"):
        return _err([f"invalid audit_scope: {audit_scope}"])

    level_name = str(config.get("level_name") or _derive_level_name(scripts_root, target_root, audit_scope))
    level_slug = _sanitize_slug(level_name)

    resolve_artifact_root = get_resolve_audit_artifact_root()
    artifact_base = resolve_artifact_root(target_root)

    steps: list[dict[str, Any]] = []
    errors: list[str] = []

    def _append_skipped(tool_name: str, reason: str) -> None:
        steps.append({"tool": tool_name, "status": "skipped", "reason": reason})

    # Tool 1: apply_violation_fixes (optional; requires scan json or audits dir)
    if "apply_violation_fixes" in tools:
        json_path = config.get("scan_json")
        audits_dir = config.get("audits_dir")
        if json_path is None and audits_dir is None:
            _append_skipped("apply_violation_fixes", "scan_json/audits_dir not provided")
        else:
            api_v = _get_api_violations()
            env = api_v.run_violation_fix_cli_api(
                {
                    "json_path": json_path,
                    "audits_dir": audits_dir,
                    "apply": bool(apply),
                    "verify": False,
                    "scripts_dev_dir": target_root,
                    "scripts_root": scripts_root,
                }
            )
            if env["status"] != "ok":
                errors.extend(env.get("errors") or [])
                steps.append({"tool": "apply_violation_fixes", "status": "error", "errors": env.get("errors")})
            else:
                steps.append({"tool": "apply_violation_fixes", "status": "ok"})

    # Tool 2: fix_imports (rewrite-only)
    if "fix_imports" in tools:
        api_m = _get_api_maintenance()
        env = api_m.run_fix_imports_cli_api(
            {
                "scripts_root": scripts_root,
                "root": target_root,
                "apply": bool(apply),
                "include_tests": bool(include_tests),
                "rewrite_relative_in_logic": str(config.get("rewrite_relative_in_logic", "off")),
                "max_changes_per_file": int(config.get("max_changes_per_file", 25) or 25),
            }
        )
        if env["status"] != "ok":
            errors.extend(env.get("errors") or [])
            steps.append({"tool": "fix_imports", "status": "error", "errors": env.get("errors")})
        else:
            steps.append({"tool": "fix_imports", "status": "ok", "data": env.get("data")})

    # Tool 3: cleanup_imports (requires report)
    if "cleanup_imports" in tools:
        report = config.get("unused_imports_report")
        if report is None:
            _append_skipped("cleanup_imports", "unused_imports_report not provided")
        else:
            api_m = _get_api_maintenance()
            env = api_m.run_unused_import_cleanup_cli_api(
                {
                    "report": report,
                    "root": target_root,
                    "dry_run": (not bool(apply)),
                    "organize_imports": (not bool(config.get("cleanup_no_organize_imports", False))),
                    "format_after": bool(config.get("cleanup_format", False)),
                    "format_tool": str(config.get("cleanup_format_tool", "ruff")),
                    "format_args": list(config.get("cleanup_format_args") or []),
                }
            )
            if env["status"] != "ok":
                errors.extend(env.get("errors") or [])
                steps.append({"tool": "cleanup_imports", "status": "error", "errors": env.get("errors")})
            else:
                steps.append({"tool": "cleanup_imports", "status": "ok", "data": env.get("data")})

    # Tool 4: organize_imports (rewrite-only)
    if "organize_imports" in tools:
        api_m = _get_api_maintenance()
        env = api_m.run_import_organizer_cli_api(
            {
                "root": target_root,
                "apply": bool(apply),
                "include_tests": bool(include_tests),
                "max_changes_per_file": int(config.get("organize_max_changes_per_file", 1) or 1),
                "max_files": config.get("organize_max_files"),
            }
        )
        if env["status"] != "ok":
            errors.extend(env.get("errors") or [])
            steps.append({"tool": "organize_imports", "status": "error", "errors": env.get("errors")})
        else:
            steps.append({"tool": "organize_imports", "status": "ok", "data": env.get("data")})

    # Tool 5: init_regen (deterministic barrels)
    if "init_regen" in tools:
        try:
            from layers.layer_2_devtools.level_1_impl.level_2 import regenerate_package_inits as rpi
        except Exception as exc:  # noqa: BLE001
            errors.append(str(exc))
            steps.append({"tool": "init_regen", "status": "error", "errors": [str(exc)]})
        else:
            argv: list[str] = ["--root", str(target_root)]
            if apply:
                argv.append("--fix")
            else:
                argv.append("--dry-run")
            if include_tests:
                argv.append("--include-tests")
            for s in list(config.get("init_exclude_symbol") or []):
                argv.extend(["--exclude-symbol", str(s)])
            for s in list(config.get("init_include_symbol") or []):
                argv.extend(["--include-symbol", str(s)])
            rc = int(rpi.main(argv))
            st = "ok" if rc == 0 else "error"
            if rc != 0:
                errors.append(f"init_regen exit_code={rc}")
            steps.append({"tool": "init_regen", "status": st, "exit_code": rc})

    # Tool 6: verify_imports (report remaining policy issues)
    verify_md_path: str | None = None
    if "verify_imports" in tools:
        api_m = _get_api_maintenance()
        env = api_m.run_verify_imports_cli_api(
            {
                "scripts_root": scripts_root,
                "root": target_root,
                "generated": generated,
                "include_tests": bool(include_tests),
                "write_json": bool(config.get("verify_write_json", False)),
            }
        )
        if env["status"] != "ok":
            errors.extend(env.get("errors") or [])
            steps.append({"tool": "verify_imports", "status": "error", "errors": env.get("errors")})
        else:
            data = env.get("data") or {}
            verify_md_path = data.get("md_path")
            steps.append({"tool": "verify_imports", "status": "ok", "data": data})

    overall_exit_code = 0 if not errors and not any(s.get("status") == "error" for s in steps) else 1

    lines: list[str] = [
        "---",
        f"generated: {_utc_now_iso()}",
        "artifact: fix_run",
        f"audit_scope: {audit_scope}",
        f"level_name: {level_name}",
        f"target_root: {target_root.as_posix()}",
        f"apply: {str(bool(apply)).lower()}",
        "---",
        "",
        "# Fix run summary",
        "",
        f"- Target: `{target_root.as_posix()}`",
        f"- Scope: `{audit_scope}`",
        f"- Apply: `{bool(apply)}`",
        "",
        "## Steps",
        "",
    ]
    for s in steps:
        tool = s.get("tool", "")
        status = s.get("status", "")
        if status == "ok":
            lines.append(f"- ✅ `{tool}`")
        elif status == "skipped":
            lines.append(f"- ⚠️ `{tool}` (skipped) — {s.get('reason','')}")
        else:
            lines.append(f"- ❌ `{tool}`")
            for e in (s.get("errors") or []):
                lines.append(f"  - {e}")
            if s.get("exit_code") is not None:
                lines.append(f"  - exit_code: {s.get('exit_code')}")
    lines.append("")
    if verify_md_path:
        lines.append("## Related artifacts")
        lines.append("")
        lines.append(f"- verify_imports report: `{verify_md_path}`")
        lines.append("")
    if errors:
        lines.append("## Errors")
        lines.append("")
        for e in errors:
            lines.append(f"- {e}")
        lines.append("")

    fix_run_path = _write_fix_run(
        artifact_base=artifact_base,
        audit_scope=audit_scope,
        level_slug=level_slug,
        generated_date=generated,
        body_lines=lines,
    )

    return _ok(
        {
            "overall_exit_code": int(overall_exit_code),
            "fix_run_path": str(fix_run_path),
            "audit_scope": audit_scope,
            "level_name": level_name,
            "level_slug": level_slug,
            "target_root": target_root.as_posix(),
            "apply": bool(apply),
            "steps": steps,
            "errors": errors,
        }
    )

