"""Environment and registry-based path utilities.

Provides convenience functions for common contest paths and
directory structures. Uses core.runtime for environment detection.
Contest selection via ContestRegistry and KAGGLE_COMP_CONTEST.
"""

import os

from pathlib import Path

from layers.layer_1_competition.level_0_infra.level_1.registry import (
    ContestRegistry,
    get_contest,
)


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
