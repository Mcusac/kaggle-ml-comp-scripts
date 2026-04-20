"""Train command builder (``python run.py`` subprocess argv shape)."""

from typing import List, Optional

from layers.layer_1_competition.level_0_infra.level_0 import (
    append_train_mode,
    resolve_and_append_models,
)
from layers.layer_1_competition.level_0_infra.level_1 import build_run_py_base_command

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    CONTEST,
    append_common_args,
)


def build_train_command(
    data_root: Optional[str] = None,
    train_mode: str = "end_to_end",
    models: Optional[List[str]] = None,
    run_id: Optional[str] = None,
    run_dir: Optional[str] = None,
    log_file: Optional[str] = None,
) -> List[str]:
    cmd = build_run_py_base_command(CONTEST, "train", data_root)
    append_train_mode(cmd, train_mode)
    resolve_and_append_models(cmd, models)
    append_common_args(cmd, run_id, run_dir, log_file)
    return cmd
