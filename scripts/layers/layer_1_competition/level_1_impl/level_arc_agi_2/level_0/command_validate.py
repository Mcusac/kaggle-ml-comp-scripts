"""Validate command builder."""

from typing import List, Optional

from layers.layer_1_competition.level_0_infra.level_1 import build_run_py_base_command

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import CONTEST


def build_validate_data_command(
    data_root: Optional[str] = None,
    max_targets: int = 0,
    log_file: Optional[str] = None,
) -> List[str]:

    cmd = build_run_py_base_command(CONTEST, "validate_data", data_root)

    if max_targets and int(max_targets) > 0:
        cmd.extend(["--max-targets", str(int(max_targets))])

    if log_file:
        cmd.extend(["--log-file", str(log_file)])

    return cmd