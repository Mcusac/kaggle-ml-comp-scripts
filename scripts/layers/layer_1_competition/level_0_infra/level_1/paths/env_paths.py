"""Environment and registry-based path utilities.

Provides convenience functions for common contest paths and
directory structures. Uses core.runtime for environment detection.
Contest selection via ContestRegistry and KAGGLE_COMP_CONTEST.
"""

import os

from pathlib import Path
from typing import Optional

from layers.layer_0_core.level_1 import get_environment_root, resolve_environment_path

from ..registry import ContestRegistry, get_contest


def get_run_py_path() -> str:
    """
    Get the path to run.py. Resolved from this file's location
    (``.../infra/level_1/paths/env_paths.py`` → ``scripts/run.py``).
    """
    scripts_dir = Path(__file__).resolve().parents[5]
    return str(scripts_dir / "run.py")


def get_data_root_path() -> str:
    """
    Get the data root for the current contest.
    Uses ContestRegistry. Contest selection: KAGGLE_COMP_CONTEST when set and
    registered; else the only registered contest; else raises.
    """
    available = ContestRegistry.list_contests()
    if not available:
        raise ValueError(
            "No contests registered. Cannot resolve data root. "
            "Pass data_root explicitly to the command builder, or ensure contest.implementations is imported."
        )

    env_contest = os.environ.get("KAGGLE_COMP_CONTEST", "").strip()
    if env_contest and env_contest in available:
        contest_name = env_contest
    elif env_contest:
        raise ValueError(
            "KAGGLE_COMP_CONTEST=%r is not a registered contest. "
            "Registered: %s" % (env_contest, ", ".join(sorted(available)))
        )
    elif len(available) == 1:
        contest_name = available[0]
    else:
        raise ValueError(
            "Multiple contests registered; data root is ambiguous. "
            f"Set KAGGLE_COMP_CONTEST to one of: {', '.join(sorted(available))}"
        )

    contest = get_contest(contest_name)
    paths_instance = contest["paths"]()
    return str(paths_instance.local_data_root)


def get_output_path(relative_path: str = "") -> Path:
    """
    Get path within the output directory.

    Args:
        relative_path: Relative path from output root (default: "")

    Returns:
        Absolute path to output location:
        - Kaggle: /kaggle/working/<relative_path>
        - Local: output/<relative_path>
    """
    if relative_path:
        return resolve_environment_path(relative_path, purpose='output')
    return get_environment_root('output')


def get_input_path(relative_path: str = "") -> Path:
    """
    Get path within the input/data directory.

    Args:
        relative_path: Relative path from data root (default: "")

    Returns:
        Absolute path to data location:
        - Kaggle: /kaggle/input/<relative_path>
        - Local: data/<relative_path>
    """
    if relative_path:
        return resolve_environment_path(relative_path, purpose='data')
    return get_environment_root('data')


def get_model_path(model_name: str, version: Optional[str] = None) -> Path:
    """
    Get path for saving/loading models.
    """
    if version:
        filename = f"{model_name}_{version}.pkl"
    else:
        filename = f"{model_name}.pkl"
    return get_output_path(f"models/{filename}")


def get_best_model_path() -> Path:
    """
    Get the path to the best_model export directory.
    """
    return get_output_path("best_model")


def get_submission_path(filename: str = "submission.csv") -> Path:
    """
    Get path for submission file.
    """
    return get_output_path(filename)


def get_checkpoint_path(experiment_name: str, epoch: int) -> Path:
    """
    Get path for model checkpoint.
    """
    return get_output_path(f"checkpoints/{experiment_name}/epoch_{epoch}.pkl")


def get_log_path(log_name: str = "training.log") -> Path:
    """
    Get path for log file.
    """
    return get_output_path(f"logs/{log_name}")
