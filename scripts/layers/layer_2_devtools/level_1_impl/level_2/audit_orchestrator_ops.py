"""Audit Orchestrator (manifest v2): compose existing devtool checks into one run.

This module must be importable without executing package ``__init__.py`` aggregators
that pull optional heavy dependencies (e.g. torch/torchvision). It uses the same
package-stubbing pattern as other devtools (e.g. circular deps) to avoid that.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Literal, TypedDict
import importlib.util
import sys

_MODULE = Path(__file__).resolve()
_SCRIPTS_ROOT = _MODULE.parents[4]


def _ensure_pkg(mod_name: str, pkg_path: Path) -> None:
    if mod_name in sys.modules:
        return
    m = ModuleType(mod_name)
    m.__path__ = [str(pkg_path)]
    sys.modules[mod_name] = m


# Avoid importing package `__init__.py` aggregators (they can pull optional deps).
_ensure_pkg("layers", _SCRIPTS_ROOT / "layers")
_ensure_pkg("layers.layer_2_devtools", _SCRIPTS_ROOT / "layers" / "layer_2_devtools")
_ensure_pkg(
    "layers.layer_2_devtools.level_0_infra",
    _SCRIPTS_ROOT / "layers" / "layer_2_devtools" / "level_0_infra",
)
_ensure_pkg(
    "layers.layer_2_devtools.level_1_impl",
    _SCRIPTS_ROOT / "layers" / "layer_2_devtools" / "level_1_impl",
)
_ensure_pkg(
    "layers.layer_2_devtools.level_1_impl.level_1",
    _SCRIPTS_ROOT / "layers" / "layer_2_devtools" / "level_1_impl" / "level_1",
)
_ensure_pkg(
    "layers.layer_2_devtools.level_1_impl.level_2",
    _SCRIPTS_ROOT / "layers" / "layer_2_devtools" / "level_1_impl" / "level_2",
)


def _load_module_from_path(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load spec for {path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


_ENVELOPE_MOD: Any = None
_PIPELINE_OPS_MOD: Any = None
_API_AUDIT_MOD: Any = None
_API_MAINT_MOD: Any = None
_API_VALIDATION_MOD: Any = None
_API_AUDIT_CHECKS_MOD: Any = None
_DISCOVERY_MOD: Any = None
_FIND_WORKSPACE_ROOT: Any = None


def _get_envelope() -> Any:
    global _ENVELOPE_MOD
    if _ENVELOPE_MOD is not None:
        return _ENVELOPE_MOD
    ep = (
        _MODULE.parents[2]
        / "level_0_infra"
        / "level_0"
        / "contracts"
        / "envelope.py"
    )
    _ENVELOPE_MOD = _load_module_from_path("devtools_envelope_audit_orchestrator", ep)
    return _ENVELOPE_MOD


_e = _get_envelope()
_err = _e.err
_ok = _e.ok
_parse_generated_optional = _e.parse_generated_optional


def _get_api_audit() -> Any:
    global _API_AUDIT_MOD
    if _API_AUDIT_MOD is not None:
        return _API_AUDIT_MOD
    p = _MODULE.parent.parent / "level_1" / "api_audit.py"
    _API_AUDIT_MOD = _load_module_from_path("devtools_api_audit_audit_orchestrator", p)
    return _API_AUDIT_MOD


def _get_api_maintenance() -> Any:
    global _API_MAINT_MOD
    if _API_MAINT_MOD is not None:
        return _API_MAINT_MOD
    p = _MODULE.parent.parent / "level_1" / "api_maintenance.py"
    _API_MAINT_MOD = _load_module_from_path(
        "devtools_api_maintenance_audit_orchestrator", p
    )
    return _API_MAINT_MOD


def _get_api_validation() -> Any:
    global _API_VALIDATION_MOD
    if _API_VALIDATION_MOD is not None:
        return _API_VALIDATION_MOD
    p = _MODULE.parent.parent / "level_1" / "api_validation.py"
    _API_VALIDATION_MOD = _load_module_from_path(
        "devtools_api_validation_audit_orchestrator", p
    )
    return _API_VALIDATION_MOD


def _get_api_audit_checks() -> Any:
    global _API_AUDIT_CHECKS_MOD
    if _API_AUDIT_CHECKS_MOD is not None:
        return _API_AUDIT_CHECKS_MOD
    p = _MODULE.parent.parent / "level_1" / "api_audit_checks.py"
    _API_AUDIT_CHECKS_MOD = _load_module_from_path(
        "devtools_api_audit_checks_audit_orchestrator", p
    )
    return _API_AUDIT_CHECKS_MOD


def _get_discovery_ops() -> Any:
    global _DISCOVERY_MOD
    if _DISCOVERY_MOD is not None:
        return _DISCOVERY_MOD
    p = _MODULE.parents[1] / "level_0" / "targets" / "discovery_ops.py"
    _DISCOVERY_MOD = _load_module_from_path(
        "devtools_audit_target_discovery_ops_audit_orchestrator", p
    )
    return _DISCOVERY_MOD


def _get_find_workspace_root() -> Callable[[Path], Path]:
    global _FIND_WORKSPACE_ROOT
    if _FIND_WORKSPACE_ROOT is not None:
        return _FIND_WORKSPACE_ROOT
    wp = (
        _MODULE.parents[2]
        / "level_0_infra"
        / "level_0"
        / "path"
        / "workspace.py"
    )
    mod = _load_module_from_path("devtools_workspace_find_audit_orchestrator", wp)
    _FIND_WORKSPACE_ROOT = mod.find_workspace_root
    return _FIND_WORKSPACE_ROOT


def _precheck_kind_cli_value(precheck_kind: str) -> str:
    if precheck_kind in ("general_level", "infra"):
        return "auto"
    return str(precheck_kind)


def _run_audit_target_discovery_core(
    *,
    scripts_root: Path,
    layers_root: Path | None,
    workspace_root: Path | None,
) -> dict[str, Any]:
    resolved_scripts_root = scripts_root.resolve()
    disc = _get_discovery_ops()
    resolved_layers_root = (
        layers_root.resolve()
        if layers_root
        else disc.default_layers_root(resolved_scripts_root)
    )
    find_root = _get_find_workspace_root()
    workspace = (
        workspace_root.resolve()
        if workspace_root
        else find_root(resolved_layers_root)
    )
    targets = disc.build_comprehensive_queue(resolved_layers_root)
    payload = disc.queue_to_json(
        targets,
        workspace=workspace,
        preset="comprehensive",
        layers_root=resolved_layers_root,
    )
    return {
        "targets": targets,
        "payload": payload,
        "json_text": disc.dumps_queue_json(payload),
        "layers_root": resolved_layers_root,
        "workspace": workspace,
    }

StepStatus = Literal["ok", "skipped", "error"]


class ArtifactRecord(TypedDict, total=False):
    kind: str
    scope: str
    level_name: str
    md_path: str
    json_path: str


class StepRecord(TypedDict, total=False):
    status: StepStatus
    errors: list[str]
    exit_code: int
    metrics: dict[str, Any]
    artifacts: list[ArtifactRecord]
    reason: str


@dataclass(frozen=True)
class StepResult:
    name: str
    record: StepRecord
    failed_step_keys: tuple[str, ...] = ()


def _default_run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")


def _resolve_output_paths(
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
    base = (
        workspace
        / ".cursor"
        / "audit-results"
        / "general"
        / "summaries"
        / "audit_orchestrator_runs"
        / run_id
    )
    return base / "manifest.json", base / "audit_queue.json"


def _step_ok(*, exit_code: int = 0, metrics: dict[str, Any] | None = None, artifacts: list[ArtifactRecord] | None = None) -> StepRecord:
    return {
        "status": "ok",
        "errors": [],
        "exit_code": int(exit_code),
        "metrics": metrics or {},
        "artifacts": artifacts or [],
    }


def _step_skipped(reason: str) -> StepRecord:
    return {"status": "skipped", "errors": [], "exit_code": 0, "metrics": {}, "artifacts": [], "reason": str(reason)}


def _step_error(errors: list[str], *, exit_code: int = 1, metrics: dict[str, Any] | None = None) -> StepRecord:
    return {"status": "error", "errors": list(errors), "exit_code": int(exit_code), "metrics": metrics or {}, "artifacts": []}


def _run_step(name: str, fn: Callable[[], dict[str, Any]]) -> StepResult:
    env = fn()
    if env.get("status") != "ok":
        errs = env.get("errors") or ["unknown error"]
        return StepResult(name=name, record=_step_error([str(e) for e in errs]), failed_step_keys=(name,))
    data = env.get("data") or {}
    exit_code = int(data.get("exit_code", 0) or 0)
    # convention: non-zero exit_code counts as a failure for the step
    failed = (name,) if exit_code != 0 else ()
    rec: StepRecord = _step_ok(exit_code=exit_code)
    return StepResult(name=name, record=rec, failed_step_keys=failed)


def run_audit_orchestrator(config: dict[str, Any]) -> dict[str, Any]:
    """Run audit orchestrator and write manifest v2.

    Config:
      - scripts_root (required): kaggle-ml-comp-scripts/scripts root
      - layers_root / workspace_root: optional overrides for discovery/workspace resolution
      - run_id: optional, default UTC YYYY-MM-DDTHHMMSSZ
      - generated: date or YYYY-MM-DD, default today
      - manifest_path or output_dir: optional output control
      - write_queue_json: bool (default True)
      - fail_on_skipped: bool (default False)
      - max_targets: optional int
      - step toggles:
          run_precheck (default True)
          run_dependency_validation (default True)
          run_import_validation (default True)
          run_circular_deps (default True)
          run_barrel_enforcement (default True)
          run_dead_symbols (default True)
    """
    try:
        try:
            scripts_root = Path(config["scripts_root"]).resolve()
        except (KeyError, TypeError) as exc:
            return _err([f"scripts_root is required: {exc}"])

        run_id = str(config.get("run_id") or _default_run_id())
        generated: date = _parse_generated_optional(config.get("generated")) or date.today()

        layers_root = Path(config["layers_root"]).resolve() if config.get("layers_root") else None
        workspace_root = Path(config["workspace_root"]).resolve() if config.get("workspace_root") else None

        write_queue = bool(config.get("write_queue_json", True))
        fail_on_skipped = bool(config.get("fail_on_skipped", False))
        max_targets = config.get("max_targets")
        max_n: int | None = int(max_targets) if max_targets is not None else None

        run_precheck = bool(config.get("run_precheck", True))
        run_dep = bool(config.get("run_dependency_validation", True))
        run_import = bool(config.get("run_import_validation", True))
        run_cycles = bool(config.get("run_circular_deps", True))
        run_barrels = bool(config.get("run_barrel_enforcement", True))
        run_dead = bool(config.get("run_dead_symbols", True))

        # Discovery + queue payload (no package __init__ imports)
        d = _run_audit_target_discovery_core(
            scripts_root=scripts_root,
            layers_root=layers_root,
            workspace_root=workspace_root,
        )
        workspace: Path = d["workspace"]
        targets = d["targets"]
        queue_payload = d["payload"]
        queue_json_text = d["json_text"]
        resolved_layers_root: Path = d["layers_root"]

        scope_counts = Counter(t.audit_scope for t in targets)
        queue_summary = {
            "target_count": len(targets),
            "by_audit_scope": dict(scope_counts),
        }

        manifest_path, queue_path = _resolve_output_paths(
            workspace=workspace,
            run_id=run_id,
            manifest_path=Path(config["manifest_path"]).resolve() if config.get("manifest_path") else None,
            output_dir=Path(config["output_dir"]).resolve() if config.get("output_dir") else None,
        )

        steps: dict[str, StepRecord] = {}
        failed_steps: list[str] = []
        skipped_steps: list[str] = []

        steps["audit_targets"] = _step_ok(
            metrics={
                "target_count": len(targets),
                "layers_root": resolved_layers_root.as_posix(),
            }
        )

        # Precheck (per target)
        if run_precheck:
            api_audit = _get_api_audit()
            slice_targets = targets if max_n is None else targets[: max(0, max_n)]
            artifacts: list[ArtifactRecord] = []
            target_ok = 0
            target_error = 0
            target_nonzero = 0
            errors: list[str] = []
            for t in slice_targets:
                env = api_audit.run_audit_precheck_cli_complete(
                    {
                        "scripts_root": scripts_root,
                        "audit_scope": t.audit_scope,
                        "level_name": t.level_name,
                        "level_path": t.level_path,
                        "workspace_root": workspace,
                        "generated": generated,
                        "precheck_kind": _precheck_kind_cli_value(t.precheck_kind),
                        "strict": bool(config.get("precheck_strict", False)),
                        "json_only": False,
                    }
                )
                if env["status"] != "ok":
                    target_error += 1
                    errors.extend([str(e) for e in env.get("errors") or []])
                    failed_steps.append(f"precheck:{t.audit_scope}:{t.level_name}")
                    continue
                data = env.get("data") or {}
                exit_code = int(data.get("exit_code", 0) or 0)
                if exit_code != 0:
                    target_nonzero += 1
                    failed_steps.append(f"precheck_exit:{t.audit_scope}:{t.level_name}")
                else:
                    target_ok += 1
                md_path = data.get("md_path")
                json_path = data.get("json_path")
                if md_path or json_path:
                    artifacts.append(
                        {
                            "kind": "precheck_summary",
                            "scope": str(t.audit_scope),
                            "level_name": str(t.level_name),
                            "md_path": str(md_path) if md_path else "",
                            "json_path": str(json_path) if json_path else "",
                        }
                    )
            status: StepStatus = "ok"
            if errors:
                status = "error"
                failed_steps.append("precheck")
            steps["precheck"] = {
                "status": status,
                "errors": errors,
                "exit_code": 1 if status == "error" else (1 if target_nonzero else 0),
                "metrics": {
                    "max_targets": max_n,
                    "target_ok": target_ok,
                    "target_error": target_error,
                    "target_nonzero_exit": target_nonzero,
                },
                "artifacts": artifacts,
            }
        else:
            steps["precheck"] = _step_skipped("run_precheck false")
            skipped_steps.append("precheck")

        # Dependency validation (layered deps)
        if run_dep:
            api_validation = _get_api_validation()
            env = api_validation.run_validate_layer_dependencies_complete(
                {
                    "scripts_root": scripts_root,
                    "include_dev": True,
                    "workspace_root": workspace,
                    "generated": generated,
                    "output_base": None,
                }
            )
            if env["status"] != "ok":
                steps["dependency_validation"] = _step_error(env.get("errors") or [])
                failed_steps.append("dependency_validation")
            else:
                data = env["data"]
                report = data.get("report") or {}
                v = report.get("violations") or {}
                steps["dependency_validation"] = _step_ok(
                    metrics={"violation_count": int(v.get("total", 0) or 0)},
                    artifacts=[
                        {
                            "kind": "dependency_validation",
                            "scope": "general",
                            "md_path": str(data.get("md_path") or ""),
                            "json_path": str(data.get("json_path") or ""),
                        }
                    ],
                )
        else:
            steps["dependency_validation"] = _step_skipped("run_dependency_validation false")
            skipped_steps.append("dependency_validation")

        # Import validation (policy) via api_maintenance verify_imports scan
        if run_import:
            api_maintenance = _get_api_maintenance()
            env = api_maintenance.run_verify_imports_cli_api(
                {
                    "scripts_root": scripts_root,
                    "root": scripts_root / "layers" / "layer_0_core",
                    "output_dir": None,
                    "generated": generated,
                    "include_tests": False,
                    "write_json": True,
                }
            )
            if env["status"] != "ok":
                steps["import_validation"] = _step_error(env.get("errors") or [])
                failed_steps.append("import_validation")
            else:
                data = env["data"]
                vcount = int(data.get("violation_count", 0) or 0)
                pecount = int(data.get("parse_error_count", 0) or 0)
                steps["import_validation"] = _step_ok(
                    metrics={"violation_count": vcount, "parse_error_count": pecount},
                    artifacts=[
                        {
                            "kind": "verify_imports_scan",
                            "scope": "general",
                            "md_path": str(data.get("md_path") or ""),
                            "json_path": str(data.get("json_path") or ""),
                        }
                    ],
                )
        else:
            steps["import_validation"] = _step_skipped("run_import_validation false")
            skipped_steps.append("import_validation")

        # Circular deps
        if run_cycles:
            api_audit_checks = _get_api_audit_checks()
            env = api_audit_checks.run_circular_deps_with_artifacts(
                {
                    "scripts_root": scripts_root,
                    "root": scripts_root,
                    "generated": generated,
                    "include_tests": False,
                    "write_json": True,
                    "output_dir": None,
                }
            )
            if env["status"] != "ok":
                steps["circular_deps"] = _step_error(env.get("errors") or [])
                failed_steps.append("circular_deps")
            else:
                data = env["data"]
                steps["circular_deps"] = _step_ok(
                    metrics={
                        "cycle_count": int(data.get("cycle_count", 0) or 0),
                        "parse_error_count": int(data.get("parse_error_count", 0) or 0),
                    },
                    artifacts=[
                        {
                            "kind": "circular_deps_scan",
                            "scope": "general",
                            "md_path": str(data.get("md_path") or ""),
                            "json_path": str(data.get("json_path") or ""),
                        }
                    ],
                )
        else:
            steps["circular_deps"] = _step_skipped("run_circular_deps false")
            skipped_steps.append("circular_deps")

        # Barrel enforcement (merged)
        if run_barrels:
            api_audit = _get_api_audit()
            env = api_audit.run_barrel_enforcement_with_artifacts(
                {
                    "scripts_dir": scripts_root,
                    "generated": generated,
                    "write_json": True,
                }
            )
            if env["status"] != "ok":
                steps["barrel_enforcement"] = _step_error(env.get("errors") or [])
                failed_steps.append("barrel_enforcement")
            else:
                data = env["data"]
                steps["barrel_enforcement"] = _step_ok(
                    metrics={
                        "violation_count": int(data.get("violation_count", 0) or 0),
                        "parse_error_count": int(data.get("parse_error_count", 0) or 0),
                    },
                    artifacts=[
                        {
                            "kind": "barrel_enforcement_scan",
                            "scope": "general",
                            "md_path": str(data.get("md_path") or ""),
                            "json_path": str(data.get("json_path") or ""),
                        }
                    ],
                )
        else:
            steps["barrel_enforcement"] = _step_skipped("run_barrel_enforcement false")
            skipped_steps.append("barrel_enforcement")

        # Dead symbols
        if run_dead:
            api_audit_checks = _get_api_audit_checks()
            env = api_audit_checks.run_dead_symbol_detector_with_artifacts(
                {
                    "scripts_root": scripts_root,
                    "root": scripts_root / "layers" / "layer_0_core",
                    "generated": generated,
                    "include_tests": False,
                    "write_json": True,
                    "output_dir": None,
                    "config_path": None,
                }
            )
            if env["status"] != "ok":
                steps["dead_symbols"] = _step_error(env.get("errors") or [])
                failed_steps.append("dead_symbols")
            else:
                data = env["data"]
                steps["dead_symbols"] = _step_ok(
                    metrics={
                        "unreferenced_count": int(data.get("unreferenced_count", 0) or 0),
                        "unreachable_count": int(data.get("unreachable_count", 0) or 0),
                    },
                    artifacts=[
                        {
                            "kind": "dead_symbol_detector_run",
                            "scope": "general",
                            "md_path": str(data.get("md_path") or ""),
                            "json_path": str(data.get("json_path") or ""),
                        }
                    ],
                )
        else:
            steps["dead_symbols"] = _step_skipped("run_dead_symbols false")
            skipped_steps.append("dead_symbols")

        if fail_on_skipped:
            for k, r in steps.items():
                if r.get("status") == "skipped":
                    reason = str(r.get("reason") or "")
                    failed_steps.append("skipped:" + k + (":" + reason if reason else ""))

        overall_exit_code = 0 if not failed_steps else 1
        generated_iso = (
            datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z")
        )

        manifest: dict[str, Any] = {
            "schema_version": "2",
            "generated": generated_iso,
            "generated_date": generated.isoformat(),
            "run_id": run_id,
            "scripts_root": scripts_root.as_posix(),
            "workspace": workspace.as_posix(),
            "layers_root": resolved_layers_root.as_posix(),
            "queue_path": queue_path.as_posix() if write_queue else None,
            "queue_stored": write_queue,
            "queue_summary": queue_summary,
            "steps": steps,
            "aggregate": {
                "overall_exit_code": overall_exit_code,
                "failed_steps": failed_steps,
                "skipped_steps": skipped_steps,
            },
        }

        try:
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
            )
            if write_queue:
                queue_path.write_text(queue_json_text, encoding="utf-8")
        except OSError as exc:
            return _err([f"failed to write manifest or queue: {exc}"])

        return _ok(
            {
                "manifest_path": str(manifest_path),
                "queue_path": str(queue_path) if write_queue else None,
                "manifest": manifest,
                "overall_exit_code": overall_exit_code,
            }
        )
    except (OSError, TypeError, ValueError) as exc:
        return _err([str(exc)])

