"""CSIRO notebook command builders — thin ``run.py`` wrappers for notebooks.

CSIRO exposes many subcommands (grid search, train, ensemble, submit, …).
Use :func:`build_run_py_command` with the subcommand name and pass extra CLI
tokens via ``extra_args`` until dedicated helpers are added.
"""

from typing import List, Optional

from layers.layer_1_competition.level_0_infra.level_1.notebook import build_run_py_base_command

from .handlers_common import CSIRO_COMMANDS

_CONTEST = "csiro"


def build_run_py_command(
    subcommand: str,
    data_root: Optional[str] = None,
    extra_args: Optional[List[str]] = None,
) -> List[str]:
    """Build argv for ``run.py`` with ``--contest csiro`` and ``--data-root``.

    Args:
        subcommand: One of :data:`CSIRO_COMMANDS` (e.g. ``submit``, ``train_and_export``).
        data_root: Optional; defaults via :func:`get_data_root_path` inside the base builder.
        extra_args: Additional CLI tokens (e.g. ``["--model", "dinov2_base"]``).

    Returns:
        Command list suitable for :func:`run_cli_streaming`.

    Raises:
        ValueError: If ``subcommand`` is not a known CSIRO command name.
    """
    if subcommand not in CSIRO_COMMANDS:
        raise ValueError(
            f"Unknown CSIRO subcommand {subcommand!r}. "
            f"Expected one of: {', '.join(sorted(CSIRO_COMMANDS))}"
        )
    cmd = build_run_py_base_command(_CONTEST, subcommand, data_root)
    if extra_args:
        cmd.extend(extra_args)
    return cmd
