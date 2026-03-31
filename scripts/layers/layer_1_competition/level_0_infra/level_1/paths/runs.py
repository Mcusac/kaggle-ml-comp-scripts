"""Shared run directory builders."""

from __future__ import annotations

from pathlib import Path

from layers.layer_1_competition.level_0_infra.level_0 import ContestPaths


def contest_runs_root(paths: ContestPaths, contest_slug: str) -> Path:
    """
    Return `<output_dir>/<contest_slug>/runs`.

    Contests can choose whether they use this convention; the builder is generic.
    """
    return paths.get_output_dir() / str(contest_slug) / "runs"


def contest_run_dir(paths: ContestPaths, contest_slug: str, run_id: str) -> Path:
    """Return `<output_dir>/<contest_slug>/runs/<run_id>`."""
    return (contest_runs_root(paths, contest_slug) / str(run_id)).resolve()


__all__ = ["contest_run_dir", "contest_runs_root"]

