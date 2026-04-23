"""Code-audit machine pipeline (lightweight import path for discovery + manifest-only runs).

``find_workspace_root`` and ``contracts/envelope`` are loaded from their ``.py`` files via
``importlib`` so ``level_0_infra`` / ``level_1`` package ``__init__`` modules are not executed
(they can pull ``layer_0_core`` and optional ``torch``/``torchvision``).
Heavy precheck/scan entrypoints are loaded lazily from ``api_audit.py`` when enabled.
"""

from __future__ import annotations

import importlib.util
import json
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable

from layers.layer_2_devtools.level_1_impl.level_0.targets.discovery_ops import AuditTarget
from layers.layer_2_devtools.level_1_impl.level_0.targets.discovery_ops import (
    build_comprehensive_queue,
    default_layers_root,
    dumps_queue_json,
    queue_to_json,
)

_FIND_WORKSPACE_ROOT: Callable[[Path], Path] | None = None
_API_AUDIT_MOD: Any = None
_ENVELOPE_MOD: Any = None


def _get_envelope() -> Any:
    """Load ``contracts/envelope.py`` from disk so ``level_0_infra`` package ``__init__`` is not run."""
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
    name = "devtools_envelope_pipeline"
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


def _get_find_workspace_root() -> Callable[[Path], Path]:
    global _FIND_WORKSPACE_ROOT
    if _FIND_WORKSPACE_ROOT is not None:
        return _FIND_WORKSPACE_ROOT
    wp = (
        Path(__file__).resolve().parents[2]
        / "level_0_infra"
        / "level_0"
        / "path"
        / "workspace.py"
    )
    name = "devtools_workspace_find_pipeline"
    spec = importlib.util.spec_from_file_location(name, wp)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load find_workspace_root from {wp}")
    mod: Any = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _FIND_WORKSPACE_ROOT = mod.find_workspace_root
    return _FIND_WORKSPACE_ROOT


def _run_audit_target_discovery_core(
    *,
    scripts_root: Path,
    layers_root: Path | None,
    workspace_root: Path | None,
) -> dict[str, Any]:
    """Same data as ``composed.audit_target_discovery_ops.run_audit_target_discovery`` (no envelope)."""
    resolved_scripts_root = scripts_root.resolve()
    resolved_layers_root = (
        layers_root.resolve() if layers_root else default_layers_root(resolved_scripts_root)
    )
    find_root = _get_find_workspace_root()
    workspace = (
        workspace_root.resolve() if workspace_root else find_root(resolved_layers_root)
    )
    targets = build_comprehensive_queue(resolved_layers_root)
    payload = queue_to_json(
        targets,
        workspace=workspace,
        preset="comprehensive",
        layers_root=resolved_layers_root,
    )
    return {
        "targets": targets,
        "payload": payload,
        "json_text": dumps_queue_json(payload),
        "layers_root": resolved_layers_root,
        "workspace": workspace,
    }


def _get_api_audit() -> Any:
    """Load ``api_audit`` from file so ``level_1`` package ``__init__`` is not executed."""
    global _API_AUDIT_MOD
    if _API_AUDIT_MOD is not None:
        return _API_AUDIT_MOD
    ap = Path(__file__).resolve().parent.parent / "level_1" / "api_audit.py"
    name = "devtools_level_1_api_audit_pipeline"
    spec = importlib.util.spec_from_file_location(name, ap)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load api_audit from {ap}")
    mod: Any = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _API_AUDIT_MOD = mod
    return mod


def _precheck_kind_cli_value(target: AuditTarget) -> str:
    if target.precheck_kind in ("general_level", "infra"):
        return "auto"
    return str(target.precheck_kind)


def _default_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")


def _resolve_manifest_and_queue_paths(
    *,
    workspace: Path,
    run_id: str,
    manifest_path: Path | None,
    output_dir: Path | None,
) -> tuple[Path, Path]:
    if manifest_path is not None:
        mp = manifest_path.resolve()
        return mp, mp.parent / "audit_queue.json"
    if output_dir is not None:
        od = output_dir.resolve()
        return od / "manifest.json", od / "audit_queue.json"
    base = workspace / ".cursor" / "audit-results" / "general" / "summaries" / "machine_runs" / run_id
    return base / "manifest.json", base / "audit_queue.json"


def run_code_audit_pipeline(config: dict[str, Any]) -> dict[str, Any]:
    """Run discovery, optional per-target prechecks, optional scans; write manifest JSON.

    Does not delete artifacts. Does not use ``tempfile``. Only creates directories and writes
    new files at deterministic paths.

    Config:
        ``scripts_root`` (required): ``kaggle-ml-comp-scripts/scripts`` root.
        ``layers_root`` / ``workspace_root``: passed to discovery (optional).
        ``run_id``: default UTC ``YYYY-MM-DDTHHMMSSZ``.
        ``generated``: date for precheck/scan filenames (default today).
        ``manifest_path`` or ``output_dir``: output location; if both omitted, uses
        ``<workspace>/.cursor/audit-results/general/summaries/machine_runs/<run_id>/``.
        ``write_queue_json`` (default True): write ``audit_queue.json`` beside manifest.
        ``run_precheck`` (default True), ``run_general_stack_scan`` (default True),
        ``run_csiro_scan`` (default True), ``run_package_boundary_validation`` (default False).
        ``precheck_strict`` (bool): ``strict`` on precheck.
        ``max_targets`` (optional int): cap precheck iterations (testing/CI).
        ``fail_on_skipped`` (bool): if True, any pipeline step with ``status: "skipped"``
        (e.g. disabled by config or missing CSIRO contest root) appends to ``failed_steps``
        and fails the aggregate.

    Returns:
        Envelope; ``data`` includes ``manifest_path``, ``queue_path`` (if written), ``manifest`` (dict).
    """
    try:
        scripts_root = Path(config["scripts_root"]).resolve()
    except (KeyError, TypeError) as exc:
        return _err([f"scripts_root is required: {exc}"])

    run_id = str(config.get("run_id") or _default_run_id())
    raw_gen = config.get("generated")
    generated: date = _parse_generated_optional(raw_gen) or date.today()

    run_precheck = bool(config.get("run_precheck", True))
    run_general = bool(config.get("run_general_stack_scan", True))
    run_csiro = bool(config.get("run_csiro_scan", True))
    run_oversized = bool(config.get("run_oversized_module_scan", True))
    run_pkg_boundary = bool(config.get("run_package_boundary_validation", False))
    precheck_strict = bool(config.get("precheck_strict", False))
    write_queue = bool(config.get("write_queue_json", True))
    max_targets = config.get("max_targets")
    max_n: int | None = int(max_targets) if max_targets is not None else None
    fail_on_skipped = bool(config.get("fail_on_skipped", False))

    layers_root = Path(config["layers_root"]).resolve() if config.get("layers_root") else None
    workspace_root = Path(config["workspace_root"]).resolve() if config.get("workspace_root") else None

    need_heavy = run_precheck or run_general or run_csiro or run_oversized or run_pkg_boundary
    api: Any = _get_api_audit() if need_heavy else None

    try:
        d = _run_audit_target_discovery_core(
            scripts_root=scripts_root,
            layers_root=layers_root,
            workspace_root=workspace_root,
        )
    except (OSError, ValueError) as exc:
        return _err([str(exc)])

    workspace: Path = d["workspace"]
    targets: list[AuditTarget] = d["targets"]
    json_text: str = d["json_text"]
    layers_root_res: Path = d["layers_root"]

    manifest_path, queue_path = _resolve_manifest_and_queue_paths(
        workspace=workspace,
        run_id=run_id,
        manifest_path=Path(config["manifest_path"]).resolve() if config.get("manifest_path") else None,
        output_dir=Path(config["output_dir"]).resolve() if config.get("output_dir") else None,
    )

    failed_steps: list[str] = []
    steps: dict[str, Any] = {
        "audit_targets": {
            "status": "ok",
            "errors": [],
            "target_count": len(targets),
            "layers_root": layers_root_res.as_posix(),
        }
    }

    scope_counts = Counter(t.audit_scope for t in targets)
    queue_summary = {
        "target_count": len(targets),
        "by_audit_scope": dict(scope_counts),
    }

    precheck_results: list[dict[str, Any]] = []
    if run_precheck:
        assert api is not None
        slice_targets = targets if max_n is None else targets[: max(0, max_n)]
        for t in slice_targets:
            env = api.run_audit_precheck_cli_complete(
                {
                    "scripts_root": scripts_root,
                    "audit_scope": t.audit_scope,
                    "level_name": t.level_name,
                    "level_path": t.level_path,
                    "workspace_root": workspace,
                    "generated": generated,
                    "precheck_kind": _precheck_kind_cli_value(t),
                    "strict": precheck_strict,
                    "json_only": False,
                }
            )
            row: dict[str, Any] = {
                "level_name": t.level_name,
                "audit_scope": t.audit_scope,
                "precheck_kind": t.precheck_kind,
            }
            if env["status"] != "ok":
                row["status"] = "error"
                row["errors"] = env["errors"]
                precheck_results.append(row)
                failed_steps.append(f"precheck:{t.audit_scope}:{t.level_name}")
            else:
                data = env["data"]
                row["status"] = "ok"
                row["exit_code"] = int(data.get("exit_code", 0))
                row["messages"] = data.get("messages", [])
                precheck_results.append(row)
                if row["exit_code"] != 0:
                    failed_steps.append(f"precheck_exit:{t.audit_scope}:{t.level_name}")
        steps["precheck"] = {
            "status": "ok" if not any(r.get("status") == "error" for r in precheck_results) else "error",
            "max_targets": max_n,
            "targets": precheck_results,
        }
    else:
        steps["precheck"] = {"status": "skipped", "reason": "run_precheck false"}

    if run_general:
        assert api is not None
        layer_0_core = scripts_root / "layers" / "layer_0_core"
        genv = api.run_general_stack_scan_with_artifacts(
            {
                "scripts_dir": layer_0_core,
                "generated": generated,
                "write_json": True,
                "workspace_root": workspace,
            }
        )
        if genv["status"] != "ok":
            steps["general_stack_scan"] = {
                "status": "error",
                "errors": genv["errors"],
            }
            failed_steps.append("general_stack_scan")
        else:
            gd = genv["data"]
            steps["general_stack_scan"] = {
                "status": "ok",
                "md_path": gd.get("md_path"),
                "json_path": gd.get("json_path"),
                "summary_line": gd.get("summary_line"),
                "exit_code": int(gd.get("exit_code", 0)),
            }
    else:
        steps["general_stack_scan"] = {"status": "skipped", "reason": "run_general_stack_scan false"}

    if run_oversized:
        assert api is not None
        oenv = api.run_oversized_module_scan_with_artifacts(
            {
                "scripts_dir": scripts_root,
                "root": scripts_root,
                "generated": generated,
                "write_json": True,
                "workspace_root": workspace,
            }
        )
        if oenv["status"] != "ok":
            steps["oversized_module_scan"] = {"status": "error", "errors": oenv["errors"]}
            failed_steps.append("oversized_module_scan")
        else:
            od = oenv["data"]
            steps["oversized_module_scan"] = {
                "status": "ok",
                "md_path": od.get("md_path"),
                "json_path": od.get("json_path"),
                "summary_line": od.get("summary_line"),
                "exit_code": int(od.get("exit_code", 0)),
                "oversized_count": int(od.get("oversized_count", 0)),
                "max_file_lines": int(od.get("max_file_lines", 0)),
            }
    else:
        steps["oversized_module_scan"] = {
            "status": "skipped",
            "reason": "run_oversized_module_scan false",
        }

    csiro_root = (
        scripts_root / "layers" / "layer_1_competition" / "level_1_impl" / "level_csiro"
    ).resolve()
    if run_csiro:
        assert api is not None
        if not csiro_root.is_dir():
            steps["csiro_scan"] = {
                "status": "skipped",
                "reason": f"contest root not a directory: {csiro_root.as_posix()}",
            }
        else:
            cenv = api.run_csiro_level_violations_cli_api(
                {
                    "scripts_dir": scripts_root,
                    "contest_slug": "level_csiro",
                    "generated": generated,
                    "write_json": True,
                }
            )
            if cenv["status"] != "ok":
                steps["csiro_scan"] = {
                    "status": "error",
                    "errors": cenv["errors"],
                }
                failed_steps.append("csiro_scan")
            else:
                cd = cenv["data"]
                steps["csiro_scan"] = {
                    "status": "ok",
                    "md_path": cd.get("md_path"),
                    "json_path": cd.get("json_path"),
                    "summary_line": cd.get("summary_line"),
                    "exit_code": int(cd.get("exit_code", 0)),
                }
                if int(cd.get("exit_code", 0)) not in (0,):
                    failed_steps.append("csiro_scan_violations")
    else:
        steps["csiro_scan"] = {"status": "skipped", "reason": "run_csiro_scan false"}

    if run_pkg_boundary:
        assert api is not None
        penv = api.run_package_boundary_validation_with_artifacts(
            {
                "scripts_root": scripts_root,
                "workspace_root": workspace,
                "scope_root": None,
                "generated": generated,
                "include_dev": True,
            }
        )
        if penv["status"] != "ok":
            steps["package_boundary_validation"] = {"status": "error", "errors": penv["errors"]}
            failed_steps.append("package_boundary_validation")
        else:
            pd = penv["data"]
            steps["package_boundary_validation"] = {
                "status": "ok",
                "md_path": pd.get("md_path"),
                "json_path": pd.get("json_path"),
                "summary_line": pd.get("summary_line"),
            }
    else:
        steps["package_boundary_validation"] = {
            "status": "skipped",
            "reason": "run_package_boundary_validation false",
        }

    if fail_on_skipped:
        for key in (
            "precheck",
            "general_stack_scan",
            "oversized_module_scan",
            "csiro_scan",
            "package_boundary_validation",
        ):
            st = steps.get(key, {})
            if st.get("status") == "skipped":
                reason = st.get("reason", "")
                failed_steps.append(
                    f"skipped:{key}" + (f":{reason}" if reason else "")
                )

    overall = 0 if not failed_steps else 1
    generated_iso = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    manifest: dict[str, Any] = {
        "schema_version": "1",
        "generated": generated_iso,
        "run_id": run_id,
        "generated_date": generated.isoformat(),
        "scripts_root": scripts_root.as_posix(),
        "workspace": workspace.as_posix(),
        "queue_path": queue_path.as_posix() if write_queue else None,
        "queue_summary": queue_summary,
        "queue_json_bytes": len(json_text.encode("utf-8")),
        "queue_stored": write_queue,
        "steps": steps,
        "aggregate": {
            "overall_exit_code": overall,
            "failed_steps": failed_steps,
        },
    }

    try:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        if write_queue:
            queue_path.write_text(json_text, encoding="utf-8")
    except OSError as exc:
        return _err([f"failed to write manifest or queue: {exc}"])

    return _ok(
        {
            "manifest_path": str(manifest_path),
            "queue_path": str(queue_path) if write_queue else None,
            "manifest": manifest,
            "overall_exit_code": overall,
        }
    )
