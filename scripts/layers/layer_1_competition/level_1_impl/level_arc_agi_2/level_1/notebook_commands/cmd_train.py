"""``train`` notebook command builder.

Shares argv primitives with ``level_1/cli/commands/build_train_command.py`` via
``level_0_infra.level_0.argv_command_builders`` (extracted in Run 12).
"""

from typing import List, Optional

from layers.layer_1_competition.level_0_infra.level_0.argv_command_builders import (
    append_run_args,
    append_train_mode,
    resolve_and_append_models,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    base_cmd,
)


def build_train_command(
    data_root: Optional[str] = None,
    train_mode: str = "end_to_end",
    models: Optional[List[str]] = None,
    run_id: Optional[str] = None,
    run_dir: Optional[str] = None,
    log_file: Optional[str] = None,
) -> List[str]:
    cmd = base_cmd("train", data_root)
    append_train_mode(cmd, train_mode)
    resolve_and_append_models(cmd, models)
    append_run_args(cmd, run_id, run_dir, log_file)
    return cmd
