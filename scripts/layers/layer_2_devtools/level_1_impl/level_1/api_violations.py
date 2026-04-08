"""Public API: violation scan driven fix workflow."""

from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_1_impl.level_0.composed.general_scan_workflow_ops import (
    ViolationFixWorkflowOptions,
    run_violation_fix_workflow as _run_violation_fix_workflow,
)
from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import err
from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import ok


def run_violation_fix_cli_api(config: dict[str, Any]) -> dict[str, Any]:
    """Run violation summary + optional bundled fixes + optional verify rescan.

    Config: ``scripts_dev_dir`` (Path), ``scripts_root`` (Path), optional ``json_path``,
        ``audits_dir``, ``apply`` (bool), ``verify`` (bool).
    """
    try:
        sdd = config.get("scripts_dev_dir")
        sr = config.get("scripts_root")
        if sdd is None or sr is None:
            return err(["scripts_dev_dir and scripts_root are required"])
        opts = ViolationFixWorkflowOptions(
            json_path=Path(config["json_path"]).resolve()
            if config.get("json_path")
            else None,
            audits_dir=Path(config["audits_dir"]).resolve()
            if config.get("audits_dir")
            else None,
            apply=bool(config.get("apply", False)),
            verify=bool(config.get("verify", False)),
            scripts_dev_dir=Path(sdd).resolve(),
            scripts_root=Path(sr).resolve(),
        )
        _run_violation_fix_workflow(opts)
        return ok({})
    except SystemExit as exc:
        code = exc.code
        if code in (None, 0):
            return ok({})
        return err([str(code) if str(code) else "workflow exited"])
    except (OSError, TypeError, ValueError) as exc:
        return err([str(exc)])


__all__ = ["run_violation_fix_cli_api"]
