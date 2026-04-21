"""``validate_data`` notebook command builder."""

from typing import List, Optional

from layers.layer_1_competition.level_0_infra.level_0.argv_command_builders import (
    append_max_targets,
    append_run_args,
)

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    base_cmd,
)


def build_validate_data_command(
    data_root: Optional[str] = None,
    max_targets: int = 0,
    log_file: Optional[str] = None,
) -> List[str]:
    cmd = base_cmd("validate_data", data_root)
    append_max_targets(cmd, max_targets)
    append_run_args(cmd, None, None, log_file)
    return cmd
