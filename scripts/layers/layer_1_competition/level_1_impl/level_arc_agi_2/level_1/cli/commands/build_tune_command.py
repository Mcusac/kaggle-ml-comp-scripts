"""Tune command builder (``python run.py`` subprocess argv shape)."""

from typing import List, Optional

from layers.layer_1_competition.level_0_infra.level_0.argv_command_builders import (
    append_max_targets,
    append_tune_args,
)
from layers.layer_1_competition.level_0_infra.level_2 import build_run_py_base_command

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.cli.append_common_args import (
    CONTEST,
    append_common_args,
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
    cmd = build_run_py_base_command(CONTEST, "tune", data_root)
    append_tune_args(cmd, model, search_type)
    append_max_targets(cmd, max_targets)
    append_common_args(cmd, run_id, run_dir, log_file)
    return cmd
