"""Public API: CI runner orchestration (pipeline + scans + health + thresholds)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import err
from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import ok
from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import parse_generated_optional
from layers.layer_2_devtools.level_1_impl.level_1 import api_audit
from layers.layer_2_devtools.level_1_impl.level_1 import api_health
from layers.layer_2_devtools.level_1_impl.level_1 import api_maintenance
from layers.layer_2_devtools.level_1_impl.level_1 import api_pipeline


@dataclass(frozen=True)
class CiRunnerStepResult:
    name: str
    exit_code: int
    status: str
    details: dict[str, Any]


def _fail_result(name: str, errors: list[str], *, exit_code: int = 2) -> CiRunnerStepResult:
    return CiRunnerStepResult(
        name=name,
        exit_code=int(exit_code),
        status="error",
        details={"errors": list(errors)},
    )


def _ok_result(name: str, *, exit_code: int = 0, **details: Any) -> CiRunnerStepResult:
    return CiRunnerStepResult(
        name=name,
        exit_code=int(exit_code),
        status="ok" if int(exit_code) == 0 else "fail",
        details=dict(details),
    )


def _parse_json_text(text: str) -> tuple[dict[str, Any] | list[Any] | None, str | None]:
    try:
        return json.loads(text), None
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        return None, str(exc)


def run_ci_runner(config: dict[str, Any]) -> dict[str, Any]:
    """Run the fast CI suite in-process.

    Config:
        ``scripts_root`` (required): path to `kaggle-ml-comp-scripts/scripts`.
        ``workspace_root`` (optional): repo root; passed to pipeline/scans to keep artifacts rooted.
        ``run_id`` (required): stable run id for manifest + summary.
        ``generated`` (optional): date (or YYYY-MM-DD); default today.
        ``strict`` (bool): strict thresholds and parse-errors gating.
        ``fail_on_skipped`` (bool): pass through to pipeline.

        ``health_root`` (required): root passed to health workflow (repo root).
        ``health_report_path`` (required): where to write health JSON (typically <workspace>/health_report.json).
        ``threshold_config_path`` (optional): threshold config JSON for health.

        ``barrel_contest_slug`` (optional, default level_csiro).

    Returns:
        Envelope where ``data`` includes per-step results, paths, and overall exit code.
    """
    try:
        scripts_root = Path(config["scripts_root"]).resolve()
    except (KeyError, TypeError) as exc:
        return err([f"scripts_root is required: {exc}"])
    try:
        health_root = Path(config["health_root"]).resolve()
        health_report_path = Path(config["health_report_path"]).resolve()
    except (KeyError, TypeError) as exc:
        return err([f"health_root and health_report_path are required: {exc}"])

    run_id = str(config.get("run_id") or "")
    if not run_id:
        return err(["run_id is required"])

    generated: date = parse_generated_optional(config.get("generated")) or date.today()
    strict = bool(config.get("strict", False))
    fail_on_skipped = bool(config.get("fail_on_skipped", False))
    threshold_config_path = (
        Path(config["threshold_config_path"]).resolve()
        if config.get("threshold_config_path")
        else None
    )
    workspace_root = (
        Path(config["workspace_root"]).resolve()
        if config.get("workspace_root")
        else None
    )

    steps: list[CiRunnerStepResult] = []

    # 1) Code audit machine pipeline (manifest + queue).
    penv = api_pipeline.run_code_audit_pipeline(
        {
            "scripts_root": scripts_root,
            "workspace_root": workspace_root,
            "run_id": run_id,
            "generated": generated,
            "precheck_strict": strict,
            "fail_on_skipped": fail_on_skipped,
        }
    )
    if penv["status"] != "ok":
        steps.append(_fail_result("code_audit_pipeline", penv["errors"]))
        manifest_path = None
    else:
        pdata = penv["data"]
        manifest_path = str(pdata.get("manifest_path") or "")
        pipeline_rc = int(pdata.get("overall_exit_code", 0))
        steps.append(
            _ok_result(
                "code_audit_pipeline",
                exit_code=pipeline_rc,
                manifest_path=manifest_path,
                queue_path=pdata.get("queue_path"),
                failed_steps=list((pdata.get("manifest") or {}).get("aggregate", {}).get("failed_steps", [])),
            )
        )

    # 2) Level violations scan (blocking).
    layer_0_core = scripts_root / "layers" / "layer_0_core"
    senv = api_audit.run_general_stack_scan_with_artifacts(
        {
            "scripts_dir": layer_0_core,
            "generated": generated,
            "write_json": True,
            "workspace_root": workspace_root,
        }
    )
    if senv["status"] != "ok":
        steps.append(_fail_result("scan_level_violations", senv["errors"]))
    else:
        sd = senv["data"]
        vcount = int(sd.get("violation_count", 0))
        pec = int(sd.get("parse_error_count", 0))
        rc = 0
        if vcount > 0:
            rc = 1
        if strict and pec > 0:
            rc = 1
        steps.append(
            _ok_result(
                "scan_level_violations",
                exit_code=rc,
                md_path=sd.get("md_path"),
                json_path=sd.get("json_path"),
                summary_line=sd.get("summary_line"),
                violation_count=vcount,
                parse_error_count=pec,
            )
        )

    # 3) Barrel enforcement scan (blocking).
    benv = api_audit.run_barrel_enforcement_with_artifacts(
        {
            "scripts_dir": scripts_root,
            "generated": generated,
            "write_json": True,
            "workspace_root": workspace_root,
            "contest_slug": str(config.get("barrel_contest_slug", "level_csiro")),
        }
    )
    if benv["status"] != "ok":
        steps.append(_fail_result("scan_barrel_enforcement", benv["errors"]))
    else:
        bd = benv["data"]
        vcount = int(bd.get("violation_count", 0))
        pec = int(bd.get("parse_error_count", 0))
        rc = 0
        if vcount > 0:
            rc = 1
        if strict and pec > 0:
            rc = 1
        steps.append(
            _ok_result(
                "scan_barrel_enforcement",
                exit_code=rc,
                md_path=bd.get("md_path"),
                json_path=bd.get("json_path"),
                summary_line=bd.get("summary_line"),
                violation_count=vcount,
                parse_error_count=pec,
            )
        )

    # 3b) Circular dependency scan (blocking).
    cenv = api_audit.run_circular_deps_scan_with_artifacts(
        {
            "root": scripts_root,
            "generated": generated,
            "write_json": True,
            "workspace_root": workspace_root,
        }
    )
    if cenv["status"] != "ok":
        steps.append(_fail_result("scan_circular_deps", cenv["errors"]))
    else:
        cd = cenv["data"]
        ccount = int(cd.get("cycle_count", 0))
        pec = int(cd.get("parse_error_count", 0))
        rc = 0
        if ccount > 0:
            rc = 1
        if strict and pec > 0:
            rc = 1
        steps.append(
            _ok_result(
                "scan_circular_deps",
                exit_code=rc,
                md_path=cd.get("md_path"),
                json_path=cd.get("json_path"),
                summary_line=cd.get("summary_line"),
                cycle_count=ccount,
                parse_error_count=pec,
            )
        )

    # 3c) Import validation (filesystem+AST) via verify_imports (blocking).
    venv = api_maintenance.run_verify_imports_cli_api(
        {
            "scripts_root": scripts_root,
            "root": scripts_root / "layers" / "layer_0_core",
            "generated": generated,
            "write_json": True,
        }
    )
    if venv["status"] != "ok":
        steps.append(_fail_result("verify_imports", venv["errors"]))
    else:
        vd = venv["data"]
        vcount = int(vd.get("violation_count", 0))
        pec = int(vd.get("parse_error_count", 0))
        rc = 0
        if vcount > 0:
            rc = 1
        if strict and pec > 0:
            rc = 1
        steps.append(
            _ok_result(
                "verify_imports",
                exit_code=rc,
                md_path=vd.get("md_path"),
                json_path=vd.get("json_path"),
                summary_line=vd.get("summary_line"),
                violation_count=vcount,
                parse_error_count=pec,
            )
        )

    # 4) Health JSON generation (same payload as `check_health --json` prints).
    henv = api_health.run_package_health_cli_api(
        {
            "root": health_root,
            "as_json": True,
            "threshold_config_path": threshold_config_path,
        }
    )
    if henv["status"] != "ok":
        steps.append(_fail_result("check_health", henv["errors"]))
    else:
        report_text = str(henv["data"]["report"])
        parsed, parse_err = _parse_json_text(report_text)
        if parse_err is not None:
            steps.append(_fail_result("check_health", [f"health json parse error: {parse_err}"]))
        else:
            health_report_path.parent.mkdir(parents=True, exist_ok=True)
            health_report_path.write_text(
                json.dumps(parsed, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            steps.append(
                _ok_result(
                    "check_health",
                    exit_code=0,
                    report_path=str(health_report_path),
                )
            )

    # 5) Threshold check (strict by default for CI runner).
    tenv = api_health.run_health_threshold_check_api(
        {
            "report_file": health_report_path,
            "threshold_config_path": threshold_config_path,
            "strict": strict,
        }
    )
    if tenv["status"] != "ok":
        steps.append(_fail_result("check_health_thresholds", tenv["errors"]))
    else:
        trc = int(tenv["data"].get("exit_code", 0))
        steps.append(_ok_result("check_health_thresholds", exit_code=trc))

    overall = 0 if all(s.exit_code == 0 for s in steps) else 1
    data = {
        "run_id": run_id,
        "generated": generated.isoformat(),
        "manifest_path": manifest_path,
        "health_report_path": str(health_report_path),
        "steps": [
            {
                "name": s.name,
                "status": s.status,
                "exit_code": s.exit_code,
                **s.details,
            }
            for s in steps
        ],
        "overall_exit_code": overall,
    }
    return ok(data)

