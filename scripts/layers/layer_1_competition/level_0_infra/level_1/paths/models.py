"""Shared model directory builders."""

from __future__ import annotations

from pathlib import Path

from layers.layer_1_competition.level_0_infra.level_0 import ContestPaths


def contest_models_dir(paths: ContestPaths, contest_slug: str) -> Path:
    """Return `<output_dir>/models/<contest_slug>` for a contest."""
    return paths.get_output_dir() / "models" / str(contest_slug)


def contest_model_dir(paths: ContestPaths, contest_slug: str, model_name: str) -> Path:
    """Return `<output_dir>/models/<contest_slug>/<model_name>`."""
    return contest_models_dir(paths, contest_slug) / str(model_name)


__all__ = ["contest_model_dir", "contest_models_dir"]

