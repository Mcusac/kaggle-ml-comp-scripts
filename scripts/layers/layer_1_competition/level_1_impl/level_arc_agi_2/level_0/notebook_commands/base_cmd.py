"""ARC notebook command base command builder."""

from typing import Optional

from layers.layer_1_competition.level_0_infra.level_1 import build_run_py_base_command

_CONTEST = "arc_agi_2"

def base_cmd(action: str, data_root: Optional[str]):
    return build_run_py_base_command(_CONTEST, action, data_root)