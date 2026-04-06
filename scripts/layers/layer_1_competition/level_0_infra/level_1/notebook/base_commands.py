"""Shared argv prefix for ``run.py`` notebook invocations (all contests)."""

import sys

from typing import List, Optional

from layers.layer_1_competition.level_0_infra.level_1.paths import (
    get_data_root_path,
    get_run_py_path,
)


def build_run_py_base_command(
    contest_name: str,
    subcommand: str,
    data_root: Optional[str] = None,
) -> List[str]:
    """Build the leading tokens for ``python run.py --contest <name> <subcommand> --data-root ...``.

    Contest-specific ``notebook_commands`` modules extend this list with their own flags.

    Args:
        contest_name: Registered contest slug (e.g. ``rna3d``, ``csiro``).
        subcommand: ``run.py`` subcommand name.
        data_root: Optional explicit data root; defaults via :func:`get_data_root_path`.
    """
    if data_root is None:
        data_root = get_data_root_path()
    return [
        sys.executable,
        get_run_py_path(),
        "--contest",
        contest_name,
        subcommand,
        "--data-root",
        str(data_root),
    ]
