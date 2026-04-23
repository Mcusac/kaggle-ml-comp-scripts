"""Public API: workspace resolution, stack scans, and audit precheck."""

import importlib.util
import json
from datetime import date
from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_0_infra.level_0.graph.import_graph import (
    build_internal_import_graph as _build_internal_import_graph,
)
from layers.layer_2_devtools.level_0_infra.level_0.graph.scc import find_cycles as _find_cycles

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
from layers.layer_2_devtools.level_0_infra.level_0.formatting.file_level_suggestions_markdown import (
    build_file_level_suggestions_markdown as _build_file_level_suggestions_markdown,
)
from layers.layer_2_devtools.level_0_infra.level_0.formatting.promotion_demotion_suggestions_markdown import (
    build_promotion_demotion_suggestions_markdown as _build_promotion_demotion_suggestions_markdown,
)
from layers.layer_2_devtools.level_0_infra.level_0.formatting.health_report_views import (
    lines_oversized_modules as _lines_oversized_modules,
)
from layers.layer_2_devtools.level_0_infra.level_1.health_analyzers.file_level_suggestion_analyzer import (
    FileLevelSuggestionAnalyzer as _FileLevelSuggestionAnalyzer,
    ScopeConfig as _ScopeConfig,
)
from layers.layer_2_devtools.level_0_infra.level_1.health_analyzers.file_metrics import (
    FileMetricsAnalyzer as _FileMetricsAnalyzer,
)
from layers.layer_2_devtools.level_0_infra.level_1.health_analyzers.promotion_demotion_suggestion_analyzer import (
    PromotionDemotionScopeConfig as _PromotionDemotionScopeConfig,
    PromotionDemotionSuggestionAnalyzer as _PromotionDemotionSuggestionAnalyzer,
)
from layers.layer_2_devtools.level_0_infra.level_0.placement.file_level_suggestions import (
    LevelPolicy as _LevelPolicy,
)
from layers.layer_2_devtools.level_0_infra.level_0.placement.promotion_demotion_suggestions import (
    HeavyReusePolicy,
)
from layers.layer_2_devtools.level_0_infra.level_0.health_thresholds import ThresholdConfig
from layers.layer_2_devtools.level_1_impl.level_1.api_validation import (
    run_validate_package_boundaries_complete,
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
        ``exit_code`` (0), ``payload`` (scan dict, including ``schema`` and violation rows),
        ``violation_count``, ``parse_error_count``.
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

        payload = result["payload"]
        data: dict[str, Any] = {
            "md_path": str(out_path),
            "exit_code": 0,
            "payload": payload,
        }
        if config.get("write_json"):
            json_path = out_path.with_suffix(".json")
            json_path.write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            data["json_path"] = str(json_path)

        total_v = sum(len(r.violations) for r in reports)
        pe = sum(1 for r in reports if r.parse_error)
        data["violation_count"] = total_v
        data["parse_error_count"] = pe
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
        out_md: Path | None = None
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
            assert out_md is not None
            snap_sources.insert(0, out_md)
        copied = _mirror_files_to_run_snapshot(
            workspace=ws,
            audit_scope=audit_scope,
            level_name=level_name,
            generated=generated,
            sources=snap_sources,
        )
        for p in copied:
            messages.append(f"[OK] Run snapshot {p}")
        return _ok(
            {
                "exit_code": 0,
                "messages": messages,
                "md_path": (str(out_md) if out_md is not None else None),
                "json_path": str(out_json),
                "snapshot_paths": [str(p) for p in copied],
                "output_base": str(out_base),
            }
        )
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


def run_barrel_enforcement_with_artifacts(config: dict[str, Any]) -> dict[str, Any]:
    """Merge general, contest, and competition-infra scans; write ``barrel_enforcement_scan_*`` artifacts.

    Config: ``scripts_dir`` (Path, folder containing ``layers/``), ``generated`` (date or str),
        optional ``layer_0_core`` (default ``<scripts_dir>/layers/layer_0_core``),
        ``contest_root`` / ``contest_slug`` (CSIRO-style defaults like :func:`run_csiro_level_violations_cli_api`),
        ``infra_level_0`` (default ``.../level_0_infra/level_0``),
        optional ``output_dir``, ``write_json`` (bool), ``run_general`` / ``run_contest`` / ``run_infra`` (bool),
        optional ``workspace_root``.

    Returns:
        Envelope; ``data`` has ``md_path``, optional ``json_path``, ``summary_line``,
        ``violation_count``, ``parse_error_count``, ``payload`` (merged v1 including ``by_scope``),
        ``exit_code`` (0).
    """
    try:
        from layers.layer_2_devtools.level_1_impl.level_0.composed.barrel_enforcement_workflow_ops import (
            run_barrel_enforcement_workflow,
        )

        scripts_dir = Path(config["scripts_dir"]).resolve()
        gen = _parse_generated_optional(config.get("generated")) or date.today()
        layer_0_core = Path(
            config.get("layer_0_core")
            or (scripts_dir / "layers" / "layer_0_core")
        ).resolve()
        contest_slug = str(config.get("contest_slug", "level_csiro"))
        cr = config.get("contest_root")
        contest_root = (
            Path(cr).resolve()
            if cr
            else (
                scripts_dir
                / "layers"
                / "layer_1_competition"
                / "level_1_impl"
                / contest_slug
            ).resolve()
        )
        ir = config.get("infra_level_0")
        infra_level_0 = (
            Path(ir).resolve()
            if ir
            else (
                scripts_dir
                / "layers"
                / "layer_1_competition"
                / "level_0_infra"
                / "level_0"
            ).resolve()
        )
        out_dir_arg = config.get("output_dir")
        run = run_barrel_enforcement_workflow(
            layer_0_core=layer_0_core,
            scripts_root=scripts_dir,
            generated=gen,
            contest_root=contest_root,
            contest_slug=contest_slug,
            infra_level_0=infra_level_0,
            run_general=bool(config.get("run_general", True)),
            run_contest=bool(config.get("run_contest", True)),
            run_infra=bool(config.get("run_infra", True)),
            workspace_root=Path(config["workspace_root"]) if config.get("workspace_root") else None,
        )
        workspace = run.workspace
        out_dir: Path
        if out_dir_arg is not None:
            out_dir = Path(out_dir_arg).resolve()
        else:
            out_dir = workspace / ".cursor" / "audit-results" / "general" / "audits"
        out_dir.mkdir(parents=True, exist_ok=True)
        stem = f"barrel_enforcement_scan_{gen.isoformat()}"
        md_path = out_dir / f"{stem}.md"
        md_path.write_text(run.markdown, encoding="utf-8")
        payload = run.merged
        vcount = int(payload.get("violation_count", 0))
        pec = int(payload.get("parse_error_count", 0))
        data: dict[str, Any] = {
            "md_path": str(md_path),
            "summary_line": (
                f"[SUMMARY] violations={vcount} | parse_errors={pec} | by_scope={payload.get('by_scope', {})!r}"
            ),
            "violation_count": vcount,
            "parse_error_count": pec,
            "payload": payload,
            "exit_code": 0,
        }
        if config.get("write_json"):
            json_path = out_dir / f"{stem}.json"
            json_path.write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            data["json_path"] = str(json_path)
        return _ok(data)
    except (OSError, TypeError, ValueError) as exc:
        return _err([str(exc)])


def _cycle_chain_for_component(
    *, component: list[str], graph: dict[str, list[str]]
) -> list[str]:
    nodes = sorted(component)
    allowed = set(nodes)
    subgraph = {n: sorted([d for d in graph.get(n, []) if d in allowed]) for n in nodes}

    if len(nodes) == 1:
        n = nodes[0]
        if n in subgraph.get(n, []):
            return [n, n]
        return [n]

    for start in nodes:
        stack: list[str] = []
        in_stack: set[str] = set()

        def dfs(v: str) -> list[str] | None:
            stack.append(v)
            in_stack.add(v)
            for w in subgraph.get(v, []):
                if w == start and len(stack) >= 2:
                    return [*stack, start]
                if w not in in_stack:
                    found = dfs(w)
                    if found is not None:
                        return found
            in_stack.remove(v)
            stack.pop()
            return None

        found = dfs(start)
        if found is not None:
            return found

    return [nodes[0], nodes[0]]


def run_circular_deps_scan_with_artifacts(config: dict[str, Any]) -> dict[str, Any]:
    """Run circular dependency scan and write MD (and optional JSON) artifacts.

    Config:
      - root: Path-like (required) root to scan for Python modules
      - generated: date or YYYY-MM-DD str (optional; default today)
      - include_tests: bool (optional; default False)
      - write_json: bool (optional; default False)
      - output_dir: Path-like (optional; default workspace/.cursor/audit-results/general/audits)

    Returns:
      Envelope; ``data`` includes ``md_path``, optional ``json_path``,
      ``cycle_count``, ``parse_error_count``, ``summary_line``, ``exit_code`` (0).
    """
    try:
        root_raw = config.get("root")
        if root_raw is None:
            return _err(["root is required"])
        root = Path(root_raw).resolve()
        if not root.is_dir():
            return _err([f"root is not a directory: {root}"])

        gen = _parse_generated_optional(config.get("generated")) or date.today()
        include_tests = bool(config.get("include_tests", False))
        write_json = bool(config.get("write_json", False))

        wenv = resolve_workspace({"start": root, "explicit_root": config.get("workspace_root")})
        if wenv["status"] != "ok":
            return wenv
        workspace: Path = wenv["data"]["workspace"]

        out_dir_arg = config.get("output_dir")
        out_dir = (
            Path(out_dir_arg).resolve()
            if out_dir_arg is not None
            else (workspace / ".cursor" / "audit-results" / "general" / "audits")
        )
        out_dir.mkdir(parents=True, exist_ok=True)

        res = _build_internal_import_graph(root=root, include_tests=include_tests)
        graph = dict(res.graph)
        parse_error_count = int(res.parse_error_count)
        components = _find_cycles(graph)
        findings = [
            {"nodes": sorted(comp), "chain": _cycle_chain_for_component(component=comp, graph=graph)}
            for comp in components
        ]
        findings.sort(key=lambda c: (len(c["nodes"]), c["nodes"]))

        payload: dict[str, Any] = {
            "schema": "circular_deps_scan.v1",
            "generated": gen.isoformat(),
            "workspace": workspace.as_posix(),
            "root": root.resolve().as_posix(),
            "include_tests": bool(include_tests),
            "parse_error_count": parse_error_count,
            "cycle_count": int(len(findings)),
            "cycles": findings,
        }

        stem = f"circular_deps_scan_{gen.isoformat()}"
        md_path = out_dir / f"{stem}.md"

        lines: list[str] = [
            "---",
            f"generated: {gen.isoformat()}",
            "artifact: circular_deps_scan",
            "schema: circular_deps_scan.v1",
            f"root: {root.resolve().as_posix()}",
            "---",
            "",
            "# Circular dependency scan",
            "",
            f"- Root: `{root.resolve().as_posix()}`",
            f"- Files with parse errors: {parse_error_count}",
            f"- Cycle components: {len(findings)}",
            "",
        ]
        if not findings:
            lines.append("✅ No circular dependencies detected.")
            lines.append("")
        else:
            lines.append("## Cycles")
            lines.append("")
            for idx, c in enumerate(findings, start=1):
                chain = " -> ".join(c["chain"])
                nodes = ", ".join(c["nodes"])
                lines.append(f"{idx}. **{len(c['nodes'])} modules**")
                lines.append(f"   - Chain: `{chain}`")
                lines.append(f"   - Nodes: `{nodes}`")
            lines.append("")

        md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        data: dict[str, Any] = {
            "md_path": str(md_path),
            "payload": payload,
            "cycle_count": int(payload["cycle_count"]),
            "parse_error_count": int(payload["parse_error_count"]),
            "summary_line": (
                f"[SUMMARY] parse_errors={payload['parse_error_count']} cycles={payload['cycle_count']}"
            ),
            "exit_code": 0,
        }
        if write_json:
            json_path = out_dir / f"{stem}.json"
            json_path.write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            data["json_path"] = str(json_path)

        return _ok(data)
    except (OSError, TypeError, ValueError, KeyError, json.JSONDecodeError) as exc:
        return _err([str(exc)])


def run_oversized_module_scan_with_artifacts(config: dict[str, Any]) -> dict[str, Any]:
    """Run oversized-module scan (file-metrics driven) and write MD/JSON artifacts.

    Config:
      - scripts_dir: Path-like, directory containing `layers/` (used for workspace resolution)
      - root: Path-like, root to analyze (defaults to scripts_dir)
      - generated: date or YYYY-MM-DD str (optional; default today)
      - threshold_config_path: optional Path-like JSON for ThresholdConfig.from_dict()
      - max_file_lines: optional int override
      - top: optional int (default 50)
      - include_suggestions: bool (default True)
      - write_json: bool (default False)
      - output_dir: Path-like (optional; default workspace/.cursor/audit-results/general/audits)
    """
    try:
        scripts_dir = Path(config["scripts_dir"]).resolve()
        root = Path(config.get("root") or scripts_dir).resolve()
        gen = _parse_generated_optional(config.get("generated")) or date.today()
        top = int(config.get("top", 50))
        include_suggestions = bool(config.get("include_suggestions", True))
        write_json = bool(config.get("write_json", False))

        wenv = resolve_workspace(
            {
                "start": scripts_dir / "layers",
                "explicit_root": config.get("workspace_root"),
            }
        )
        if wenv["status"] != "ok":
            return wenv
        workspace: Path = wenv["data"]["workspace"]

        tc_path = (
            Path(config["threshold_config_path"]).resolve()
            if config.get("threshold_config_path")
            else None
        )
        tc = ThresholdConfig()
        if tc_path and tc_path.is_file():
            tc = ThresholdConfig.from_dict(json.loads(tc_path.read_text(encoding="utf-8")))
        max_file_lines = (
            int(config["max_file_lines"])
            if config.get("max_file_lines") is not None
            else int(getattr(tc, "max_file_lines", 500))
        )

        metrics = _FileMetricsAnalyzer(root).analyze()
        report_data: dict[str, Any] = {"root": str(root.resolve()), "file_metrics": metrics}
        oversized = [
            r
            for r in (metrics.get("long_files") or [])
            if isinstance(r, dict) and int(r.get("lines", 0) or 0) > max_file_lines
        ]
        oversized_count = len(oversized)

        out_dir_arg = config.get("output_dir")
        out_dir = (
            Path(out_dir_arg).resolve()
            if out_dir_arg is not None
            else (workspace / ".cursor" / "audit-results" / "general" / "audits")
        )
        out_dir.mkdir(parents=True, exist_ok=True)
        stem = f"oversized_module_scan_{gen.isoformat()}"
        md_path = out_dir / f"{stem}.md"

        body_lines = _lines_oversized_modules(
            report_data,
            report_path=md_path,
            max_file_lines=max_file_lines,
            top=top,
            include_suggestions=include_suggestions,
        )

        header = [
            "---",
            f"generated: {gen.isoformat()}",
            "artifact: oversized_module_scan",
            "schema: oversized_module_scan.v1",
            f"root: {root.resolve().as_posix()}",
            f"max_file_lines: {max_file_lines}",
            f"oversized_count: {oversized_count}",
            f"threshold_config_path: {(tc_path.as_posix() if tc_path else None)}",
            "---",
            "",
            "# Oversized module scan",
            "",
        ]
        md_path.write_text(
            "\n".join([*header, *body_lines]).rstrip("\n") + "\n",
            encoding="utf-8",
        )

        data: dict[str, Any] = {
            "md_path": str(md_path),
            "oversized_count": oversized_count,
            "max_file_lines": max_file_lines,
            "exit_code": 0,
            "summary_line": (
                f"[SUMMARY] oversized={oversized_count} max_file_lines={max_file_lines}"
            ),
            "payload": {
                "schema": "oversized_module_scan.v1",
                "generated": gen.isoformat(),
                "workspace": workspace.as_posix(),
                "root": root.resolve().as_posix(),
                "max_file_lines": max_file_lines,
                "oversized_count": oversized_count,
                "oversized": [
                    {"module": str(r.get('module') or 'unknown'), "lines": int(r.get('lines', 0) or 0)}
                    for r in oversized[:200]
                    if isinstance(r, dict)
                ],
            },
        }
        if write_json:
            json_path = out_dir / f"{stem}.json"
            json_path.write_text(
                json.dumps(data["payload"], indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            data["json_path"] = str(json_path)

        return _ok(data)
    except (OSError, TypeError, ValueError, KeyError, json.JSONDecodeError) as exc:
        return _err([str(exc)])


def run_file_level_suggestions_with_artifacts(config: dict[str, Any]) -> dict[str, Any]:
    """Run file level suggestion analysis and write MD (and optional JSON).

    Config:
      - scripts_dir: Path-like, directory containing `layers/`
      - scope: general|contests|infra
      - root: Path-like (scope root containing level_N dirs)
      - generated: date or YYYY-MM-DD str (optional; default today)
      - include: optional list of Path-like include roots (relative or absolute)
      - exclude: optional list of Path-like exclude roots
      - write_json: bool (optional)
      - output_dir: Path-like (optional; default workspace/.cursor/audit-results/<scope>/audits)
      - strict: bool (optional) -> exit_code 1 if any conflict rows
      - policy: optional dict {min_level_delta_for_outgoing, max_level_delta_for_incoming}
      - import_prefixes: optional list[str]
    """
    try:
        scripts_dir = Path(config["scripts_dir"]).resolve()
        scope = str(config.get("scope", "general"))
        root = Path(config["root"]).resolve()
        gen = _parse_generated_optional(config.get("generated")) or date.today()
        include = tuple(Path(p).resolve() for p in (config.get("include") or []))
        exclude = tuple(Path(p).resolve() for p in (config.get("exclude") or []))
        write_json = bool(config.get("write_json", False))
        strict = bool(config.get("strict", False))
        import_prefixes = tuple(str(s) for s in (config.get("import_prefixes") or ()))

        pol = config.get("policy") or {}
        policy = _LevelPolicy(
            min_level_delta_for_outgoing=int(pol.get("min_level_delta_for_outgoing", 1)),
            max_level_delta_for_incoming=int(pol.get("max_level_delta_for_incoming", -1)),
        )

        wenv = resolve_workspace(
            {
                "start": scripts_dir / "layers",
                "explicit_root": config.get("workspace_root"),
            }
        )
        if wenv["status"] != "ok":
            return wenv
        workspace: Path = wenv["data"]["workspace"]

        analyzer = _FileLevelSuggestionAnalyzer(
            root,
            config=_ScopeConfig(
                scope=scope,
                root=root,
                include=include,
                exclude=exclude,
                import_prefixes=import_prefixes,
                policy=policy,
            ),
        )
        analyzed = analyzer.analyze()
        payload: dict[str, Any] = {
            "generated": gen.isoformat(),
            "artifact": "file_level_suggestions",
            "schema": "file_level_suggestions.v1",
            **analyzed,
        }
        md = _build_file_level_suggestions_markdown(payload)

        out_dir_arg = config.get("output_dir")
        out_dir = (
            Path(out_dir_arg).resolve()
            if out_dir_arg is not None
            else (workspace / ".cursor" / "audit-results" / scope / "audits")
        )
        out_dir.mkdir(parents=True, exist_ok=True)
        stem = f"file_level_suggestions_{scope}_{gen.isoformat()}"
        md_path = out_dir / f"{stem}.md"
        md_path.write_text(md, encoding="utf-8")

        data: dict[str, Any] = {
            "md_path": str(md_path),
            "payload": payload,
            "summary_line": f"[SUMMARY] scope={scope} rows={len(payload.get('rows', []))} counts={payload.get('counts', {})!r}",
            "exit_code": 0,
        }
        if write_json:
            json_path = out_dir / f"{stem}.json"
            json_path.write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            data["json_path"] = str(json_path)

        conflict_count = int((payload.get("counts") or {}).get("conflict", 0))
        if strict and conflict_count > 0:
            data["exit_code"] = 1

        return _ok(data)
    except (OSError, TypeError, ValueError, KeyError) as exc:
        return _err([str(exc)])


def run_promotion_demotion_suggestions_with_artifacts(config: dict[str, Any]) -> dict[str, Any]:
    """Run promotion/demotion suggestion analysis and write MD (and optional JSON).

    Config:
      - scripts_dir: Path-like, directory containing `layers/`
      - scope: general|contests|infra
      - root: Path-like (scope root containing level_N dirs)
      - generated: date or YYYY-MM-DD str (optional; default today)
      - include: optional list of Path-like include roots (relative or absolute)
      - exclude: optional list of Path-like exclude roots
      - write_json: bool (optional)
      - output_dir: Path-like (optional; default workspace/.cursor/audit-results/<scope>/audits)
      - strict: bool (optional) -> exit_code 1 if any ok rows exist (promotion or demotion)
      - heavy_reuse_policy: optional dict {min_total_inbound, min_distinct_importers, min_distinct_levels}
      - top_importers_limit: optional int
      - import_prefixes: optional list[str]
    """
    try:
        scripts_dir = Path(config["scripts_dir"]).resolve()
        scope = str(config.get("scope", "general"))
        root = Path(config["root"]).resolve()
        gen = _parse_generated_optional(config.get("generated")) or date.today()
        include = tuple(Path(p).resolve() for p in (config.get("include") or []))
        exclude = tuple(Path(p).resolve() for p in (config.get("exclude") or []))
        write_json = bool(config.get("write_json", False))
        strict = bool(config.get("strict", False))
        import_prefixes = tuple(str(s) for s in (config.get("import_prefixes") or ()))

        hr = config.get("heavy_reuse_policy") or {}
        heavy_policy = HeavyReusePolicy(
            min_total_inbound=int(hr.get("min_total_inbound", 10)),
            min_distinct_importers=int(hr.get("min_distinct_importers", 5)),
            min_distinct_levels=int(hr.get("min_distinct_levels", 2)),
        )
        top_importers_limit = int(config.get("top_importers_limit", 10))

        wenv = resolve_workspace(
            {
                "start": scripts_dir / "layers",
                "explicit_root": config.get("workspace_root"),
            }
        )
        if wenv["status"] != "ok":
            return wenv
        workspace: Path = wenv["data"]["workspace"]

        analyzer = _PromotionDemotionSuggestionAnalyzer(
            root,
            config=_PromotionDemotionScopeConfig(
                scope=scope,
                root=root,
                include=include,
                exclude=exclude,
                import_prefixes=import_prefixes,
                heavy_reuse_policy=heavy_policy,
                top_importers_limit=top_importers_limit,
            ),
        )
        analyzed = analyzer.analyze()
        payload: dict[str, Any] = {
            "generated": gen.isoformat(),
            "artifact": "promotion_demotion_suggestions",
            "schema": "promotion_demotion_suggestions.v1",
            **analyzed,
        }
        md = _build_promotion_demotion_suggestions_markdown(payload)

        out_dir_arg = config.get("output_dir")
        out_dir = (
            Path(out_dir_arg).resolve()
            if out_dir_arg is not None
            else (workspace / ".cursor" / "audit-results" / scope / "audits")
        )
        out_dir.mkdir(parents=True, exist_ok=True)
        stem = f"promotion_demotion_suggestions_{scope}_{gen.isoformat()}"
        md_path = out_dir / f"{stem}.md"
        md_path.write_text(md, encoding="utf-8")

        data: dict[str, Any] = {
            "md_path": str(md_path),
            "payload": payload,
            "summary_line": (
                f"[SUMMARY] scope={scope} "
                f"promotion_ok={int((payload.get('counts', {}).get('promotion', {}) or {}).get('ok', 0))} "
                f"demotion_ok={int((payload.get('counts', {}).get('demotion', {}) or {}).get('ok', 0))}"
            ),
            "exit_code": 0,
        }
        if write_json:
            json_path = out_dir / f"{stem}.json"
            json_path.write_text(
                json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            data["json_path"] = str(json_path)

        if strict:
            promo_ok = int((payload.get("counts", {}).get("promotion", {}) or {}).get("ok", 0))
            demo_ok = int((payload.get("counts", {}).get("demotion", {}) or {}).get("ok", 0))
            if promo_ok > 0 or demo_ok > 0:
                data["exit_code"] = 1

        return _ok(data)
    except (OSError, TypeError, ValueError, KeyError) as exc:
        return _err([str(exc)])


def run_package_boundary_validation_with_artifacts(config: dict[str, Any]) -> dict[str, Any]:
    """Run package boundary validation and write JSON/MD artifacts.

    Config: ``scripts_root`` (required), optional ``workspace_root``, ``scope_root``,
    ``generated`` (date or str), ``include_dev`` (bool; default True).
    """
    try:
        sr = config.get("scripts_root")
        if sr is None:
            return _err(["scripts_root is required"])
        env = run_validate_package_boundaries_complete(
            {
                "scripts_root": Path(sr),
                "workspace_root": config.get("workspace_root"),
                "scope_root": config.get("scope_root"),
                "generated": config.get("generated"),
                "include_dev": bool(config.get("include_dev", True)),
                "output_base": None,
            }
        )
        if env["status"] != "ok":
            return env
        data = env["data"]
        return _ok(
            {
                "md_path": data.get("md_path"),
                "json_path": data.get("json_path"),
                "summary_line": data.get("summary_line"),
            }
        )
    except (OSError, TypeError, ValueError) as exc:
        return _err([str(exc)])