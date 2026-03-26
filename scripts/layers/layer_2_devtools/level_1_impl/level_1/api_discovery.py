"""Public API: audit target discovery."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_1_impl.level_0.composed.audit_target_discovery_ops import (
    resolve_default_layers_root as _resolve_default_layers_root,
)
from layers.layer_2_devtools.level_1_impl.level_0.composed.audit_target_discovery_ops import (
    run_audit_target_discovery as _run_audit_target_discovery,
)
from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import err as _err
from layers.layer_2_devtools.level_0_infra.level_0.contracts.envelope import ok as _ok


def run_audit_target_discovery(config: dict[str, Any]) -> dict[str, Any]:
    """Run audit target discovery (Step 1e queue).

    Args:
        config: Optional keys ``preset`` (default ``comprehensive``), ``scripts_root``,
            ``layers_root``, ``workspace_root`` (``Path`` or str), ``include_markdown`` (bool).

    Returns:
        ``{"status": "ok"|"error", "data": {...}, "errors": [...]}``. On success,
        ``data`` matches composed output: ``targets``, ``payload``, ``json_text``,
        ``layers_root``, ``workspace``, optional ``markdown``.
    """
    try:
        preset = str(config.get("preset", "comprehensive"))
        scripts_root = _optional_path(config.get("scripts_root"))
        layers_root = _optional_path(config.get("layers_root"))
        workspace_root = _optional_path(config.get("workspace_root"))
        include_markdown = bool(config.get("include_markdown", False))
        raw = _run_audit_target_discovery(
            preset=preset,
            scripts_root=scripts_root,
            layers_root=layers_root,
            workspace_root=workspace_root,
            include_markdown=include_markdown,
        )
        return _ok(raw)
    except ValueError as exc:
        return _err([str(exc)])


def resolve_default_layers_root_api(config: dict[str, Any]) -> dict[str, Any]:
    """Resolve ``scripts/layers`` from scripts root.

    Args:
        config: Must include ``scripts_root`` (``Path`` or str).

    Returns:
        Envelope with ``data["layers_root"]`` as ``Path`` on success.
    """
    try:
        sr = config.get("scripts_root")
        if sr is None:
            return _err(["scripts_root is required"])
        path = _resolve_default_layers_root(Path(sr))
        return _ok({"layers_root": path})
    except (TypeError, ValueError) as exc:
        return _err([str(exc)])


def _optional_path(value: Any) -> Path | None:
    if value is None:
        return None
    return Path(value)


def run_audit_targets_cli_complete(config: dict[str, Any]) -> dict[str, Any]:
    """Discovery CLI: optional manifest write, JSON stdout, optional markdown.

    Config: ``scripts_root``, ``preset``, optional ``layers_root``, ``workspace_root``,
        ``markdown``, ``json_only``, ``write_manifest`` (Path or None).
    """
    try:
        scripts_root = Path(config["scripts_root"])
        preset = str(config.get("preset", "comprehensive"))
        layers_root: Path | None
        if config.get("layers_root"):
            layers_root = Path(config["layers_root"]).resolve()
        else:
            lr = resolve_default_layers_root_api({"scripts_root": scripts_root})
            if lr["status"] != "ok":
                return lr
            layers_root = lr["data"]["layers_root"]

        markdown_flag = bool(config.get("markdown", False))
        json_only = bool(config.get("json_only", False))
        out = run_audit_target_discovery(
            {
                "preset": preset,
                "layers_root": layers_root,
                "workspace_root": config.get("workspace_root"),
                "include_markdown": markdown_flag and not json_only,
            }
        )
        if out["status"] != "ok":
            return out
        result = out["data"]
        stderr_messages: list[str] = []
        wm = config.get("write_manifest")
        if wm:
            wp = Path(wm)
            wp.parent.mkdir(parents=True, exist_ok=True)
            wp.write_text(result["json_text"], encoding="utf-8")
            stderr_messages.append(f"[OK] Wrote manifest {wp}")

        return _ok(
            {
                "exit_code": 0,
                "json_text": result["json_text"],
                "markdown": result.get("markdown"),
                "stderr_messages": stderr_messages,
                "print_markdown_after": markdown_flag and not json_only,
            }
        )
    except (OSError, TypeError, ValueError) as exc:
        return _err([str(exc)])


__all__ = [
    "resolve_default_layers_root_api",
    "run_audit_target_discovery",
    "run_audit_targets_cli_complete",
]
