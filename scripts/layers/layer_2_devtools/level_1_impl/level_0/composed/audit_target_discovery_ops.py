"""Audit target discovery composed workflow."""

from pathlib import Path
from typing import Any

from layers.layer_2_devtools.level_1_impl.level_0.targets.discovery_ops import (
    build_comprehensive_queue,
    build_markdown_table,
    default_layers_root,
    dumps_queue_json,
    queue_to_json,
)
from layers.layer_2_devtools.level_0_infra.level_0.path.workspace import find_workspace_root


def run_audit_target_discovery(
    *,
    preset: str = "comprehensive",
    scripts_root: Path | None = None,
    layers_root: Path | None = None,
    workspace_root: Path | None = None,
    include_markdown: bool = False,
) -> dict[str, Any]:
    """Build deterministic audit target payload and optional markdown."""
    resolved_scripts_root = scripts_root.resolve() if scripts_root else None
    resolved_layers_root = (
        layers_root.resolve()
        if layers_root
        else default_layers_root(resolved_scripts_root)  # type: ignore[arg-type]
    )
    if preset != "comprehensive":
        raise ValueError(f"Unsupported preset: {preset}")
    workspace = (
        workspace_root.resolve() if workspace_root else find_workspace_root(resolved_layers_root)
    )
    targets = build_comprehensive_queue(resolved_layers_root)
    payload = queue_to_json(
        targets,
        workspace=workspace,
        preset=preset,
        layers_root=resolved_layers_root,
    )
    output: dict[str, Any] = {
        "targets": targets,
        "payload": payload,
        "json_text": dumps_queue_json(payload),
        "layers_root": resolved_layers_root,
        "workspace": workspace,
    }
    if include_markdown:
        output["markdown"] = build_markdown_table(targets, workspace=workspace)
    return output


def resolve_default_layers_root(scripts_root: Path) -> Path:
    """Resolve default layers root from scripts root."""
    return default_layers_root(scripts_root.resolve())