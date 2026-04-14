"""Shared submission output path builders."""

from pathlib import Path

from layers.layer_1_competition.level_0_infra.level_0 import ContestPaths


def contest_submission_path(paths: ContestPaths, filename: str) -> Path:
    """Return `<output_dir>/<filename>`."""
    return paths.get_output_dir() / str(filename)