"""Public API: pre-upload contest import validation."""

from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_1_impl.level_0.composed.pre_upload_validation_workflow_ops import (
    run_pre_upload_validation as _run_pre_upload_validation,
)
from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import err
from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import ok


def run_pre_upload_validation_cli_api(config: dict[str, Any]) -> dict[str, Any]:
    """Discover contest modules and run import validation.

    Config: ``scripts_root`` (Path), optional ``verbose`` (bool).
    """
    try:
        sr = config.get("scripts_root")
        if sr is None:
            return err(["scripts_root is required"])
        rc = _run_pre_upload_validation(
            Path(sr).resolve(),
            verbose=bool(config.get("verbose", False)),
        )
        return ok({"exit_code": int(rc)})
    except (OSError, TypeError, ValueError) as exc:
        return err([str(exc)])


__all__ = ["run_pre_upload_validation_cli_api"]
