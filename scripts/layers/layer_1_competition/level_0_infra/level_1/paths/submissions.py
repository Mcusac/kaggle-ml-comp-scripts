"""Shared submission output path builders."""

from __future__ import annotations

from pathlib import Path

from layers.layer_1_competition.level_0_infra.level_0 import ContestPaths


def contest_submission_path(paths: ContestPaths, filename: str) -> Path:
    """Return `<output_dir>/<filename>`."""
    return paths.get_output_dir() / str(filename)


__all__ = ["contest_submission_path"]

