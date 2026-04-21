"""``tune`` notebook command builder.

Shares argv primitives with ``level_1/cli/commands/build_tune_command.py`` via
``level_0_infra.level_0.argv_command_builders`` (extracted in Run 12).
"""

from typing import List, Optional

from layers.layer_1_competition.level_0_infra.level_0 import (
    append_max_targets,
    append_run_args,
    append_tune_args,
)

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    base_cmd,
)


def build_tune_command(
    data_root: Optional[str] = None,
    model: str = "baseline_approx",
    search_type: str = "quick",
    max_targets: int = 0,
    run_id: Optional[str] = None,
    run_dir: Optional[str] = None,
    log_file: Optional[str] = None,
) -> List[str]:
    cmd = base_cmd("tune", data_root)
    append_tune_args(cmd, model, search_type)
    append_max_targets(cmd, max_targets)
    append_run_args(cmd, run_id, run_dir, log_file)
    return cmd
