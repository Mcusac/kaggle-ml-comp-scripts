"""Train command builder."""

from typing import List, Optional

from layers.layer_1_competition.level_0_infra.level_1 import build_run_py_base_command

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import append_common_args, CONTEST


def build_train_command(
    data_root: Optional[str] = None,
    train_mode: str = "end_to_end",
    models: Optional[List[str]] = None,
    run_id: Optional[str] = None,
    run_dir: Optional[str] = None,
    log_file: Optional[str] = None,
) -> List[str]:

    model_names = models or ["baseline_approx"]
    cmd = build_run_py_base_command(CONTEST, "train", data_root)

    cmd.extend(["--train-mode", str(train_mode)])
    cmd.extend(["--models", ",".join(model_names)])

    append_common_args(cmd, run_id, run_dir, log_file)

    return cmd