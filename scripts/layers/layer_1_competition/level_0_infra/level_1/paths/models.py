"""Shared model directory builders."""

from pathlib import Path

from layers.layer_1_competition.level_0_infra.level_0 import ContestPaths, contest_models_dir


def contest_model_dir(paths: ContestPaths, contest_slug: str, model_name: str) -> Path:
    """Return `<output_dir>/models/<contest_slug>/<model_name>`."""
    return contest_models_dir(paths, contest_slug) / str(model_name)


__all__ = ["contest_model_dir", "contest_models_dir"]

