"""Public API: workspace resolution, stack scans, and audit precheck."""

import importlib.util
import json
from datetime import date
from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_1_impl.level_0.composed.audit_precheck_workflow_ops import (
    dumps_precheck_payload as _dumps_precheck_payload,
)
from layers.layer_2_devtools.level_1_impl.level_0.composed.audit_precheck_workflow_ops import (
    run_general_full_precheck as _run_general_full_precheck,
)
from layers.layer_2_devtools.level_1_impl.level_0.composed.audit_precheck_workflow_ops import (
    run_target_precheck as _run_target_precheck,
)
from layers.layer_2_devtools.level_1_impl.level_0.composed.contest_scan_workflow_ops import (
    run_contest_tier_scan_workflow as _run_contest_tier_scan,
)
from layers.layer_2_devtools.level_1_impl.level_0.composed.general_scan_workflow_ops import (
    run_general_scan_workflow as _run_general_scan,
)
from layers.layer_2_devtools.level_0_infra.level_0.path.audit_paths import (
    mirror_files_to_run_snapshot as _mirror_files_to_run_snapshot,
)
from layers.layer_2_devtools.level_0_infra.level_0.path.workspace import (
    resolve_workspace_root as _resolve_workspace_root,
)
from layers.layer_2_devtools.level_0_infra.level_1.rollup_skeleton import (
    build_comprehensive_rollup_skeleton_markdown as _build_rollup_skeleton,
)
from layers.layer_2_devtools.level_0_infra.level_0.path.layer_core_paths import (
    find_layer_0_core_ancestor,
)
from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import err as _err
from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import ok as _ok
from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import parse_generated as _parse_generated
from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import (
    parse_generated_optional as _parse_generated_optional,
)

_precheck_validate_fn: Any = None


def _validate_precheck_json_file(data: dict[str, Any]) -> list[str]:
    """Load ``precheck_json_contract`` by path (no ``from ...models`` import)."""
    global _precheck_validate_fn
    if _precheck_validate_fn is None:
        contract = (
            Path(__file__).resolve().parent.parent.parent
            / "level_0_infra"
            / "level_0"
            / "models"
            / "precheck_json_contract.py"
        )
        name = "precheck_json_contract_api_audit"
        spec = importlib.util.spec_from_file_location(name, contract)
        if spec is None or spec.loader is None:
            return [f"cannot load precheck contract: {contract}"]
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _precheck_validate_fn = mod.validate_precheck_json
    return _precheck_validate_fn(data)


def resolve_workspace(config: dict[str, Any]) -> dict[str, Any]:
    """Resolve repository workspace root.

    Args:
        config: ``start`` (Path or str, required), optional ``explicit_root``.

    Returns:
        Envelope; ``data["workspace"]`` is the resolved ``Path``.
    """
    try:
        st = config.get("start")
        if st is None:
            return _err(["start is required"])
        explicit = config.get("explicit_root")
        ws = _resolve_workspace_root(
            Path(st),
            Path(explicit) if explicit is not None else None,
        )
        return _ok({"workspace": ws})
    except (OSError, TypeError, ValueError) as exc:
        return _err([str(exc)])


def build_comprehensive_rollup_skeleton(config: dict[str, Any]) -> dict[str, Any]:
    """Build audit rollup skeleton markdown from a target queue payload.

    Args:
        config: ``queue`` (dict), ``workspace`` (Path-like), ``generated`` (date or str),
            ``run_id``, ``user_request_placeholder``.

    Returns:
        Envelope with ``data["markdown"]``.
    """
    try:
        queue = config.get("queue")
        if queue is None:
            return _err(["queue is required"])
        ws = config.get("workspace")
        if ws is None:
            return _err(["workspace is required"])
        gen = _parse_generated(config.get("generated"))
        rid = config.get("run_id", "rollup-skeleton")
        ur = config.get("user_request_placeholder", "")
        md = _build_rollup_skeleton(
            queue,
            Path(ws),
            gen,
            run_id=str(rid),
            user_request_placeholder=str(ur),
        )
        return _ok({"markdown": md})
    except (OSError, TypeError, ValueError) as exc:
        return _err([str(exc)])


def resolve_layer_0_core(config: dict[str, Any]) -> dict[str, Any]:
    """Find nearest ``layer_0_core`` directory ancestor.

    Args:
        config: ``start`` — path-like anchor (file or directory).

    Returns:
        Envelope; on success ``data["layer_0_core"]`` is the resolved ``Path``.
    """
    try:
        st = config.get("start")
        if st is None:
            return _err(["start is required"])
        found = find_layer_0_core_ancestor(Path(st))
        if found is None:
            return _err(["no layer_0_core directory in ancestor chain"])
        return _ok({"layer_0_core": found})
    except (OSError, TypeError, ValueError) as exc:
        return _err([str(exc)])


def run_general_stack_scan(config: dict[str, Any]) -> dict[str, Any]:
    """Scan general stack (layer_0..level_10) for import violations.

    Args:
        config: ``scripts_dir`` (Path or str), ``generated`` (date or ``YYYY-MM-DD`` str),
            optional ``workspace_root``.

    Returns:
        Envelope; ``data`` contains ``files``, ``reports``, ``markdown``, ``payload``, ``workspace``.
    """
    try:
        sd = config.get("scripts_dir")
        if sd is None:
            return _err(["scripts_dir is required"])
        gen = _parse_generated(config.get("generated"))
        workspace_root = Path(config["workspace_root"]) if config.get("workspace_root") else None
        result = _run_general_scan(Path(sd), generated=gen, workspace_root=workspace_root)
        return _ok(
            {
                "files": result.files,
                "reports": result.reports,
                "markdown": result.markdown,
                "payload": result.payload,
                "workspace": result.workspace,
            }
        )
    except (OSError, TypeError, ValueError) as exc:
        return _err([str(exc)])


def run_contest_tier_scan(config: dict[str, Any]) -> dict[str, Any]:
    """Scan contest tier directories for import violations.

    Args:
        config: ``scripts_dir``, ``contest_root``, ``contest_slug``, ``generated``,
            optional ``workspace_root``.

    Returns:
        Envelope; ``data`` has ``reports``, ``payload``, ``markdown``, ``workspace``.
    """
    try:
        for key in ("scripts_dir", "contest_root", "contest_slug"):
            if config.get(key) is None:
                return _err([f"{key} is required"])
        gen = _parse_generated(config.get("generated"))
        workspace_root = Path(config["workspace_root"]) if config.get("workspace_root") else None
        result = _run_contest_tier_scan(
            scripts_dir=Path(config["scripts_dir"]),
            contest_root=Path(config["contest_root"]),
            contest_slug=str(config["contest_slug"]),
            generated=gen,
            workspace_root=workspace_root,
        )
        return _ok(
            {
                "reports": result.reports,
                "payload": result.payload,
                "markdown": result.markdown,
                "workspace": result.workspace,
            }
        )
    except (OSError, TypeError, ValueError) as exc:
        return _err([str(exc)])


def run_audit_precheck(config: dict[str, Any]) -> dict[str, Any]:
    """Run audit precheck (full general stack or single target).

    Args:
        config: ``mode`` — ``full_general`` or ``target``.

        For ``full_general``: ``layer_0_core``, ``level_name``, ``generated``,
            optional ``workspace_root``.

        For ``target``: ``audit_scope``, ``level_path``, ``level_name``, ``generated``,
            optional ``workspace_root``, ``precheck_kind`` (default ``auto``).

    Returns:
        Envelope; ``data`` has ``reports``, ``markdown``, ``payload``, ``workspace``, ``output_base``.
    """
    try:
        mode = config.get("mode")
        if mode == "full_general":
            gen = _parse_generated(config.get("generated"))
            lc = config.get("layer_0_core")
            ln = config.get("level_name")
            if lc is None or ln is None:
                return _err(["layer_0_core and level_name are required for full_general"])
            workspace_root = Path(config["workspace_root"]) if config.get("workspace_root") else None
            result = _run_general_full_precheck(
                layer_0_core=Path(lc),
                generated=gen,
                level_name=str(ln),
                workspace_root=workspace_root,
            )
        elif mode == "target":
            gen = _parse_generated(config.get("generated"))
            for key in ("audit_scope", "level_path", "level_name"):
                if config.get(key) is None:
                    return _err([f"{key} is required for target"])
            workspace_root = Path(config["workspace_root"]) if config.get("workspace_root") else None
            result = _run_target_precheck(
                audit_scope=str(config["audit_scope"]),
                level_path=Path(config["level_path"]),
                level_name=str(config["level_name"]),
                generated=gen,
                workspace_root=workspace_root,
                precheck_kind=str(config.get("precheck_kind", "auto")),
            )
        else:
            return _err(['mode must be "full_general" or "target"'])
        return _ok(
            {
                "reports": result.reports,
                "markdown": result.markdown,
                "payload": result.payload,
                "workspace": result.workspace,
                "output_base": result.output_base,
            }
        )
    except (OSError, TypeError, ValueError) as exc:
        return _err([str(exc)])


def serialize_precheck_payload(config: dict[str, Any]) -> dict[str, Any]:
    """Serialize precheck payload dict to deterministic JSON text.

    Args:
        config: ``payload`` — the precheck payload dict.

    Returns:
        Envelope; ``data["json_text"]`` is the string.
    """
    try:
        payload = config.get("payload")
        if payload is None:
            return _err(["payload is required"])
        text = _dumps_precheck_payload(payload)
        return _ok({"json_text": text})
    except (TypeError, ValueError) as exc:
        return _err([str(exc)])


def run_general_stack_scan_with_artifacts(config: dict[str, Any]) -> dict[str, Any]:
    """Scan general stack, write markdown (and optional JSON), return paths and summary.

    Config: ``scripts_dir``, ``generated`` (date or str), optional ``output`` (Path with suffix
    for explicit .md path), optional ``write_json`` (bool).

    Returns:
        Envelope; ``data`` includes ``md_path``, optional ``json_path``, ``summary_line``,
        ``exit_code`` (0).
    """
    try:
        sd = config.get("scripts_dir")
        if sd is None:
            return _err(["scripts_dir is required"])
        gen = _parse_generated(config.get("generated"))
        workspace_root = Path(config["workspace_root"]) if config.get("workspace_root") else None
        env = run_general_stack_scan(
            {
                "scripts_dir": Path(sd),
                "generated": gen,
                "workspace_root": workspace_root,
            }
        )
        if env["status"] != "ok":
            return env
        result = env["data"]
        workspace: Path = result["workspace"]
        out_arg = config.get("output")
        if out_arg is not None and Path(out_arg).suffix:
            out_path = Path(out_arg).resolve()
        else:
            out_dir = workspace / ".cursor/audit-results/general/audits"
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / f"level_violations_scan_{gen.isoformat()}.md"

        md = result["markdown"]
        files = result["files"]
        reports = result["reports"]
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(md, encoding="utf-8")

        data: dict[str, Any] = {
            "md_path": str(out_path),
            "exit_code": 0,
        }
        if config.get("write_json"):
            json_path = out_path.with_suffix(".json")
            payload = result["payload"]
            json_path.write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            data["json_path"] = str(json_path)

        total_v = sum(len(r.violations) for r in reports)
        pe = sum(1 for r in reports if r.parse_error)
        data["summary_line"] = (
            f"[SUMMARY] Files scanned: {len(files)} | "
            f"Violations: {total_v} | Parse errors: {pe}"
        )
        return _ok(data)
    except (OSError, TypeError, ValueError) as exc:
        return _err([str(exc)])


def _violations_report_stem(contest_slug: str) -> str:
    if contest_slug.startswith("level_"):
        return f"{contest_slug[6:]}_level_violations"
    return f"{contest_slug}_level_violations"


def run_contest_tier_scan_with_artifacts(config: dict[str, Any]) -> dict[str, Any]:
    """Contest tier scan with writes and process exit code in ``data.exit_code``.

    Config: ``scripts_dir``, ``contest_root``, ``contest_slug``, ``generated``,
    optional ``output_dir`` (default: ``workspace/.cursor/audit-results/contests/audits``),
    ``write_json`` (bool).

    Returns:
        Envelope; ``data`` has ``exit_code`` 0/1/3 and ``md_path`` (and optional ``json_path``).
    """
    try:
        contest_root = Path(config.get("contest_root") or "")
        if not contest_root.is_dir():
            return _err([f"contest_root is not a directory: {contest_root}"])

        gen = _parse_generated(config.get("generated"))
        workspace_root = Path(config["workspace_root"]) if config.get("workspace_root") else None
        env = run_contest_tier_scan(
            {
                "scripts_dir": Path(config["scripts_dir"]),
                "contest_root": contest_root,
                "contest_slug": str(config["contest_slug"]),
                "generated": gen,
                "workspace_root": workspace_root,
            }
        )
        if env["status"] != "ok":
            return env
        result = env["data"]
        workspace: Path = result["workspace"]
        out_dir_arg = config.get("output_dir")
        out_dir = (
            Path(out_dir_arg).resolve()
            if out_dir_arg is not None
            else (workspace / ".cursor" / "audit-results" / "contests" / "audits")
        )
        out_dir.mkdir(parents=True, exist_ok=True)
        slug = str(config["contest_slug"])
        stem = _violations_report_stem(slug)
        md_path = out_dir / f"{stem}_{gen.isoformat()}.md"
        md_path.write_text(result["markdown"].rstrip("\n") + "\n", encoding="utf-8")
        data: dict[str, Any] = {"md_path": str(md_path)}
        if config.get("write_json"):
            json_path = md_path.with_suffix(".json")
            json_path.write_text(
                json.dumps(result["payload"], indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            data["json_path"] = str(json_path)

        all_reports = result["reports"]
        upward = result["payload"]["contest_upward"]
        other = result["payload"]["other_violations"]
        pe = sum(1 for r in all_reports if r.parse_error)
        data["summary_line"] = (
            f"[SUMMARY] Parse errors: {pe} | CONTEST_UPWARD: {len(upward)} | other: {len(other)}"
        )
        if pe:
            data["exit_code"] = 3
        elif upward:
            data["exit_code"] = 1
        else:
            data["exit_code"] = 0
        return _ok(data)
    except (OSError, TypeError, ValueError) as exc:
        return _err([str(exc)])


def build_audit_rollup_from_queue_path(config: dict[str, Any]) -> dict[str, Any]:
    """Read queue JSON from disk, resolve workspace, build rollup skeleton markdown.

    Config: ``queue_path`` (Path), ``scripts_root`` (Path, for default layers anchor),
        optional ``workspace_root``, ``generated`` (date or str), ``run_id``, ``user_request``,
        optional ``output`` (Path to write markdown; omit to return markdown only).
    """
    try:
        qp = config.get("queue_path")
        sr = config.get("scripts_root")
        if qp is None or sr is None:
            return _err(["queue_path and scripts_root are required"])
        qpath = Path(qp).resolve()
        queue = json.loads(qpath.read_text(encoding="utf-8"))
        scripts_root = Path(sr)
        layers_root_str = queue.get("layers_root")
        start = (
            Path(layers_root_str).resolve()
            if layers_root_str
            else scripts_root / "layers"
        )
        wenv = resolve_workspace(
            {
                "start": start,
                "explicit_root": config.get("workspace_root"),
            }
        )
        if wenv["status"] != "ok":
            return wenv
        workspace = wenv["data"]["workspace"]
        raw_gen = config.get("generated")
        if raw_gen is not None:
            generated = _parse_generated_optional(raw_gen)
            if generated is None:
                generated = date.today()
        else:
            generated = date.today()
        roll = build_comprehensive_rollup_skeleton(
            {
                "queue": queue,
                "workspace": workspace,
                "generated": generated,
                "run_id": str(config.get("run_id", "rollup-skeleton")),
                "user_request_placeholder": str(
                    config.get("user_request", "_(paste USER_REQUEST here)_")
                ),
            }
        )
        if roll["status"] != "ok":
            return roll
        md = roll["data"]["markdown"]
        out = config.get("output")
        if out:
            outp = Path(out)
            outp.parent.mkdir(parents=True, exist_ok=True)
            outp.write_text(md, encoding="utf-8")
            return _ok({"markdown": md, "output_path": str(outp), "wrote_file": True})
        return _ok({"markdown": md, "wrote_file": False})
    except (json.JSONDecodeError, OSError, TypeError, ValueError) as exc:
        return _err([str(exc)])


def run_audit_precheck_cli_complete(config: dict[str, Any]) -> dict[str, Any]:
    """Run precheck and write markdown/JSON artifacts (CLI orchestration).

    Config: ``scripts_root``, ``audit_scope``, ``level_name``, optional ``level_path``,
        ``workspace_root``, ``generated`` (date or YYYY-MM-DD), ``json_only`` (bool),
        ``full_general_scan`` (bool), ``precheck_kind`` (str).
    """
    try:
        scripts_root = Path(config["scripts_root"])
        strict_validate = bool(config.get("strict"))
        generated = _parse_generated_optional(config.get("generated")) or date.today()
        default_layer_core = scripts_root / "layers" / "layer_0_core"
        full_general = bool(config.get("full_general_scan", False))
        audit_scope = str(config["audit_scope"])
        level_name = str(config["level_name"])
        workspace_root = Path(config["workspace_root"]) if config.get("workspace_root") else None
        json_only = bool(config.get("json_only", False))
        precheck_kind = str(config.get("precheck_kind", "auto"))

        messages: list[str] = []

        if full_general:
            if audit_scope != "general":
                return _err(["--full-general-scan requires audit-scope general"])
            lp = config.get("level_path")
            layer_core = Path(lp).resolve() if lp else default_layer_core.resolve()
            if layer_core.name != "layer_0_core":
                core_env = resolve_layer_0_core({"start": layer_core})
                layer_core = (
                    core_env["data"]["layer_0_core"]
                    if core_env["status"] == "ok"
                    else default_layer_core.resolve()
                )
            env = run_audit_precheck(
                {
                    "mode": "full_general",
                    "layer_0_core": layer_core,
                    "level_name": level_name,
                    "generated": generated,
                    "workspace_root": workspace_root,
                }
            )
        else:
            if not config.get("level_path"):
                return _err(["level_path is required unless full_general_scan"])
            level_path = Path(config["level_path"]).resolve()
            env = run_audit_precheck(
                {
                    "mode": "target",
                    "audit_scope": audit_scope,
                    "level_path": level_path,
                    "level_name": level_name,
                    "generated": generated,
                    "workspace_root": workspace_root,
                    "precheck_kind": precheck_kind,
                }
            )
        if env["status"] != "ok":
            return env
        result = env["data"]
        md = result["markdown"]
        payload = result["payload"]
        out_base = result["output_base"]
        out_dir = out_base.parent
        out_dir.mkdir(parents=True, exist_ok=True)
        if not json_only:
            out_md = Path(str(out_base) + ".md")
            out_md.write_text(md, encoding="utf-8")
            messages.append(f"[OK] Wrote {out_md}")
        out_json = Path(str(out_base) + ".json")
        sj = serialize_precheck_payload({"payload": payload})
        if sj["status"] != "ok":
            return sj
        out_json.write_text(sj["data"]["json_text"], encoding="utf-8")
        messages.append(f"[OK] Wrote {out_json}")
        if strict_validate:
            parsed = json.loads(out_json.read_text(encoding="utf-8"))
            v_errs = _validate_precheck_json_file(parsed)
            if v_errs:
                return _err([f"precheck JSON contract: {e}" for e in v_errs])
        ws = Path(result["workspace"])
        snap_sources: list[Path] = [out_json]
        if not json_only:
            snap_sources.insert(0, Path(str(out_base) + ".md"))
        copied = _mirror_files_to_run_snapshot(
            workspace=ws,
            audit_scope=audit_scope,
            level_name=level_name,
            generated=generated,
            sources=snap_sources,
        )
        for p in copied:
            messages.append(f"[OK] Run snapshot {p}")
        return _ok({"exit_code": 0, "messages": messages})
    except (OSError, TypeError, ValueError) as exc:
        return _err([str(exc)])


def run_csiro_level_violations_cli_api(config: dict[str, Any]) -> dict[str, Any]:
    """CSIRO contest scan with default contest root under ``layer_1_competition/level_1_impl``."""
    try:
        scripts_dir = Path(config["scripts_dir"])
        slug = str(config.get("contest_slug", "level_csiro"))
        cr = config.get("contest_root")
        contest_root = (
            Path(cr).resolve()
            if cr
            else (
                scripts_dir
                / "layers"
                / "layer_1_competition"
                / "level_1_impl"
                / slug
            ).resolve()
        )
        generated = _parse_generated_optional(config.get("generated")) or date.today()
        merged = {
            "scripts_dir": scripts_dir,
            "contest_root": contest_root,
            "contest_slug": slug,
            "generated": generated,
            "output_dir": Path(config["output_dir"]).resolve() if config.get("output_dir") else None,
            "write_json": bool(config.get("write_json", False)),
        }
        return run_contest_tier_scan_with_artifacts(merged)
    except (OSError, TypeError, ValueError) as exc:
        return _err([str(exc)])