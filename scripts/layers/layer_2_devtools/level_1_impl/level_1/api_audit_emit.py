"""Public API: comprehensive audit machine emit (manifest loop)."""

from datetime import date
from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_1_impl.level_0.composed.audit_precheck_workflow_ops import (
    run_comprehensive_audit_emit as _run_comprehensive_audit_emit,
)
from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import err
from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import ok


def run_comprehensive_audit_emit_cli_api(config: dict[str, Any]) -> dict[str, Any]:
    """Emit inventory/audit markdown from a manifest; returns process exit code.

    Config: ``manifest`` (Path), ``scripts_root`` (Path), optional ``workspace_root``,
        ``generated`` (date or ``YYYY-MM-DD``), ``run_id``, ``pass_number``, ``skip_precheck``.
    """
    try:
        manifest = config.get("manifest")
        scripts_root = config.get("scripts_root")
        if manifest is None or scripts_root is None:
            return err(["manifest and scripts_root are required"])
        raw_gen = config.get("generated")
        if raw_gen is None:
            generated = date.today()
        elif isinstance(raw_gen, date):
            generated = raw_gen
        else:
            generated = date.fromisoformat(str(raw_gen))
        try:
            rc = _run_comprehensive_audit_emit(
                manifest=Path(manifest).resolve(),
                workspace_override=Path(config["workspace_root"]).resolve()
                if config.get("workspace_root")
                else None,
                generated=generated,
                run_id=str(config.get("run_id", "comprehensive-emit")),
                pass_number=int(config.get("pass_number", 1)),
                skip_precheck=bool(config.get("skip_precheck", False)),
                scripts_root=Path(scripts_root).resolve(),
            )
        except SystemExit as exc:
            code = exc.code
            if isinstance(code, int):
                return ok({"exit_code": code})
            return err([str(code) if code else "comprehensive_audit_emit failed"])
        return ok({"exit_code": int(rc)})
    except (OSError, TypeError, ValueError) as exc:
        return err([str(exc)])


__all__ = ["run_comprehensive_audit_emit_cli_api"]
