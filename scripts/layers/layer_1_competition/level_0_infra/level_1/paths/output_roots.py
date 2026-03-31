"""Contest output root builders."""

from __future__ import annotations

from pathlib import Path

from layers.layer_1_competition.level_0_infra.level_0 import ContestPaths


def contest_output_root(paths: ContestPaths) -> Path:
    """Return the contest's output root directory."""
    return paths.get_output_dir()


__all__ = ["contest_output_root"]

