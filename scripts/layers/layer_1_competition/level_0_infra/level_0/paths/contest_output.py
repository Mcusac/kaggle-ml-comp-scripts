"""Generic contest output directory helpers."""

from pathlib import Path

from layers.layer_1_competition.level_0_infra.level_0.abstractions.paths import ContestPaths


def contest_models_dir(paths: ContestPaths, contest_slug: str) -> Path:
    """Return `<output_dir>/models/<contest_slug>` for a contest."""
    return paths.get_output_dir() / "models" / str(contest_slug)
