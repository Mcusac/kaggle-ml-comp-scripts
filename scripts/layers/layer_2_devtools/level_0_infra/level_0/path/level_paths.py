"""Atomic level path parsers for devtools validation.

This module must be importable without triggering cross-package initialization
cycles inside `layers.layer_2_devtools.level_0_infra`.
"""

from pathlib import Path

from ..constants.import_patterns import LEVEL_DIR_RE


def file_level_from_path(path: Path, scripts_dir: Path) -> int | None:
    """Return numeric N from first segment matching level_N under scripts_dir."""
    try:
        relative_path = path.resolve().relative_to(scripts_dir.resolve())
    except ValueError:
        return None
    for part in relative_path.parts:
        match = LEVEL_DIR_RE.fullmatch(part)
        if match:
            return int(match.group(1))
    return None


def infra_tier_from_level_dir(level_dir: Path) -> int | None:
    """Return numeric K when directory name is level_K."""
    match = LEVEL_DIR_RE.fullmatch(level_dir.name)
    return int(match.group(1)) if match else None


def contest_tier_from_path(path: Path, contest_dir: Path) -> int | None:
    """Return numeric K for file under .../contests/<slug>/level_K/..."""
    try:
        relative_path = path.resolve().relative_to(contest_dir.resolve())
    except ValueError:
        return None
    for part in relative_path.parts:
        match = LEVEL_DIR_RE.fullmatch(part)
        if match:
            return int(match.group(1))
    return None


__all__ = ["file_level_from_path", "infra_tier_from_level_dir", "contest_tier_from_path"]

