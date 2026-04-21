"""Shared command utilities (CONTEST constant + run-metadata arg appender).

``append_common_args`` delegates to :func:`notebook_commands.arg_common.append_run_args`
to avoid duplicated logic; both entry points are preserved for backward compatibility.
"""

from typing import List, Optional

from layers.layer_1_competition.level_0_infra.level_0.argv_command_builders import (
    append_run_args,
)

CONTEST = "arc_agi_2"


def append_common_args(
    cmd: List[str],
    run_id: Optional[str],
    run_dir: Optional[str],
    log_file: Optional[str],
) -> None:
    append_run_args(cmd, run_id, run_dir, log_file)
