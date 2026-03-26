"""Public API: layered dependency validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_1_impl.level_1.composed.dependency_validation_ops import (
    run_dependency_validation_workflow as _run_dependency_validation,
    write_dependency_report_artifacts as _write_dependency_report_artifacts,
)
from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import err as _err
from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import ok as _ok
from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import (
    parse_generated_optional as _parse_generated_optional,
)


def run_dependency_validation(config: dict[str, Any]) -> dict[str, Any]:
    """Build dependency graph and violation report.

    Args:
        config: ``scripts_root`` (required), optional ``include_dev`` (default True),
            ``workspace_root``, ``generated`` (``date`` or ``YYYY-MM-DD`` str).

    Returns:
        Envelope; on success ``data["report"]`` is the full report dict (includes
        ``workspace``, ``violations``, ``markdown``, ``edges``, etc.).
    """
    try:
        sr = config.get("scripts_root")
        if sr is None:
            return _err(["scripts_root is required"])
        scripts_root = Path(sr)
        include_dev = bool(config.get("include_dev", True))
        workspace_root = Path(config["workspace_root"]) if config.get("workspace_root") else None
        generated = _parse_generated_optional(config.get("generated"))
        report = _run_dependency_validation(
            scripts_root=scripts_root,
            include_dev=include_dev,
            workspace_root=workspace_root,
            generated=generated,
        )
        return _ok({"report": report})
    except (OSError, TypeError, ValueError) as exc:
        return _err([str(exc)])


def write_dependency_reports(config: dict[str, Any]) -> dict[str, Any]:
    """Write JSON and markdown artifacts for a validation report.

    Args:
        config: ``report`` (dict from ``run_dependency_validation`` data.report),
            ``workspace`` (Path or str), optional ``output_base`` (Path or str).

    Returns:
        Envelope with ``data["json_path"]``, ``data["md_path"]`` as str paths.
    """
    try:
        report = config.get("report")
        if report is None:
            return _err(["report is required"])
        ws = config.get("workspace")
        if ws is None:
            return _err(["workspace is required"])
        ob = config.get("output_base")
        json_path, md_path = _write_dependency_report_artifacts(
            report,
            workspace=Path(ws),
            output_base=Path(ob) if ob is not None else None,
        )
        return _ok({"json_path": str(json_path), "md_path": str(md_path)})
    except (OSError, TypeError, ValueError) as exc:
        return _err([str(exc)])


def run_validate_layer_dependencies_complete(config: dict[str, Any]) -> dict[str, Any]:
    """Validate layered deps, write JSON/MD artifacts, return paths and summary fields.

    Config: ``scripts_root`` (required), optional ``include_dev`` (default True),
        ``workspace_root``, ``generated`` (date or ``YYYY-MM-DD`` str), ``output_base``.

    Returns:
        Envelope; on success ``data`` has ``json_path``, ``md_path``, ``summary_line``, and
        ``report`` (validation report dict).
    """
    vr = run_dependency_validation(
        {
            "scripts_root": config.get("scripts_root"),
            "include_dev": bool(config.get("include_dev", True)),
            "workspace_root": config.get("workspace_root"),
            "generated": config.get("generated"),
        }
    )
    if vr["status"] != "ok":
        return vr
    report = vr["data"]["report"]
    workspace = Path(report["workspace"]).resolve()
    ob = config.get("output_base")
    wr = write_dependency_reports(
        {
            "report": report,
            "workspace": workspace,
            "output_base": Path(ob).resolve() if ob is not None else None,
        }
    )
    if wr["status"] != "ok":
        return wr
    v = report["violations"]
    summary = (
        "[SUMMARY] "
        f"files={report['files_scanned']} imports={report['imports_analyzed']} "
        f"violations={v['total']} "
        f"(same={v['same_level']} upward={v['upward']} "
        f"illegal_external={v['illegal_external']}) "
        f"todos={len(report['todos'])}"
    )
    return _ok(
        {
            "report": report,
            "json_path": wr["data"]["json_path"],
            "md_path": wr["data"]["md_path"],
            "summary_line": summary,
        }
    )


__all__ = [
    "run_dependency_validation",
    "run_validate_layer_dependencies_complete",
    "write_dependency_reports",
]
