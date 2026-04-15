"""Tune command builder."""

from typing import List, Optional

from layers.layer_1_competition.level_0_infra.level_1 import build_run_py_base_command

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import append_common_args, CONTEST


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

    cmd.extend(["--model", str(model)])
    cmd.extend(["--search-type", str(search_type)])

    if max_targets and int(max_targets) > 0:
        cmd.extend(["--max-targets", str(int(max_targets))])

    append_common_args(cmd, run_id, run_dir, log_file)

    return cmd