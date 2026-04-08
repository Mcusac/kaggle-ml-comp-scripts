"""Composed audit target discovery operations using level_0 primitives."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from layers.layer_2_devtools.level_0_infra.level_0.constants.import_patterns import LEVEL_DIR_RE

AuditScope = Literal["general", "competition_infra", "contests_special"]


@dataclass(frozen=True)
class AuditTarget:
    """One deterministic target for audit planning operations."""

    audit_scope: AuditScope
    level_name: str
    level_path: Path
    level_number: int
    segment_id: str
    segment_index: int
    target_index: int
    precheck_kind: Literal["general_level", "infra", "contest_tier", "contest_root", "special_tree"]

    def to_json_dict(self, *, workspace: Path | None = None) -> dict[str, Any]:
        path = self.level_path.resolve()
        payload: dict[str, Any] = {
            "audit_scope": self.audit_scope,
            "level_name": self.level_name,
            "level_path": path.as_posix(),
            "level_number": self.level_number,
            "segment_id": self.segment_id,
            "segment_index": self.segment_index,
            "target_index": self.target_index,
            "precheck_kind": self.precheck_kind,
        }
        if workspace is not None:
            try:
                payload["level_path_relative"] = path.relative_to(workspace.resolve()).as_posix()
            except ValueError:
                payload["level_path_relative"] = None
        return payload


def default_layers_root(scripts_root: Path) -> Path:
    """Return the resolved `scripts/layers` root from scripts root."""
    return (scripts_root / "layers").resolve()


def build_comprehensive_queue(layers_root: Path) -> list[AuditTarget]:
    """Build comprehensive deterministic target queue by scope segment."""
    root = layers_root.resolve()
    targets: list[AuditTarget] = []
    target_idx = 0
    segment_idx = 0

    layer_0_core = root / "layer_0_core"
    for level, level_path in _sorted_level_dirs(layer_0_core, max_n=10):
        targets.append(
            AuditTarget(
                audit_scope="general",
                level_name=f"level_{level}",
                level_path=level_path,
                level_number=level,
                segment_id="general",
                segment_index=segment_idx,
                target_index=target_idx,
                precheck_kind="general_level",
            )
        )
        target_idx += 1
    segment_idx += 1

    infra_root = root / "layer_1_competition" / "level_0_infra"
    for level, level_path in _sorted_level_dirs(infra_root):
        targets.append(
            AuditTarget(
                audit_scope="competition_infra",
                level_name=f"level_{level}",
                level_path=level_path,
                level_number=level,
                segment_id="competition_infra",
                segment_index=segment_idx,
                target_index=target_idx,
                precheck_kind="infra",
            )
        )
        target_idx += 1
    segment_idx += 1

    level_1_impl_root = root / "layer_1_competition" / "level_1_impl"
    if level_1_impl_root.is_dir():
        contest_names = sorted(
            path.name
            for path in level_1_impl_root.iterdir()
            if path.is_dir() and path.name != "__pycache__"
        )
        for contest_name in contest_names:
            contest_path = level_1_impl_root / contest_name
            segment_id = f"contests_special:{contest_name}"
            for level, level_path in _sorted_level_dirs(contest_path):
                targets.append(
                    AuditTarget(
                        audit_scope="contests_special",
                        level_name=f"{contest_name}_level_{level}",
                        level_path=level_path,
                        level_number=level,
                        segment_id=segment_id,
                        segment_index=segment_idx,
                        target_index=target_idx,
                        precheck_kind="contest_tier",
                    )
                )
                target_idx += 1
            if _contest_has_root_py(contest_path):
                targets.append(
                    AuditTarget(
                        audit_scope="contests_special",
                        level_name=f"{contest_name}_root",
                        level_path=contest_path,
                        level_number=0,
                        segment_id=segment_id,
                        segment_index=segment_idx,
                        target_index=target_idx,
                        precheck_kind="contest_root",
                    )
                )
                target_idx += 1
            segment_idx += 1

    z_path = root / "layer_Z_unsorted"
    if z_path.is_dir():
        targets.append(
            AuditTarget(
                audit_scope="contests_special",
                level_name="layer_Z_unsorted",
                level_path=z_path,
                level_number=0,
                segment_id="contests_special:layer_Z_unsorted",
                segment_index=segment_idx,
                target_index=target_idx,
                precheck_kind="special_tree",
            )
        )
    return targets


def queue_to_json(
    targets: list[AuditTarget],
    *,
    workspace: Path | None = None,
    preset: str = "comprehensive",
    layers_root: Path | None = None,
) -> dict[str, Any]:
    """Render queue to normalized JSON payload."""
    return {
        "preset": preset,
        "layers_root": layers_root.resolve().as_posix() if layers_root else None,
        "target_count": len(targets),
        "targets": [target.to_json_dict(workspace=workspace) for target in targets],
    }


def dumps_queue_json(obj: dict[str, Any]) -> str:
    """Dump queue JSON in deterministic order."""
    return json.dumps(obj, indent=2, sort_keys=False)


def build_markdown_table(targets: list[AuditTarget], workspace: Path | None = None) -> str:
    """Build markdown table view for queue targets."""
    lines = [
        "| # | segment | scope | level_name | level_path |",
        "|---|---------|-------|------------|------------|",
    ]
    for target in targets:
        path = target.level_path.resolve()
        if workspace is not None:
            try:
                display = path.relative_to(workspace.resolve()).as_posix()
            except ValueError:
                display = path.as_posix()
        else:
            display = path.as_posix()
        lines.append(
            f"| {target.target_index} | {target.segment_id} | {target.audit_scope} | "
            f"`{target.level_name}` | `{display}` |"
        )
    return "\n".join(lines) + "\n"


def _sorted_level_dirs(parent: Path, *, max_n: int | None = None) -> list[tuple[int, Path]]:
    rows: list[tuple[int, Path]] = []
    if not parent.is_dir():
        return rows
    for child in parent.iterdir():
        if not child.is_dir() or child.name == "__pycache__":
            continue
        match = LEVEL_DIR_RE.fullmatch(child.name)
        if not match:
            continue
        n = int(match.group(1))
        if max_n is not None and n > max_n:
            continue
        rows.append((n, child))
    rows.sort(key=lambda row: row[0])
    return rows


def _contest_has_root_py(contest_dir: Path) -> bool:
    if not contest_dir.is_dir():
        return False
    return any(path.is_file() and path.suffix == ".py" for path in contest_dir.iterdir())


__all__ = [
    "AuditScope",
    "AuditTarget",
    "default_layers_root",
    "build_comprehensive_queue",
    "queue_to_json",
    "dumps_queue_json",
    "build_markdown_table",
]
