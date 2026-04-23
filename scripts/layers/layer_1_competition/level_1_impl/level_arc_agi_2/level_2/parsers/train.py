"""Register the ``train`` subparser."""

from typing import Any

from layers.layer_1_competition.level_0_infra.level_0 import add_max_targets_arg
from layers.layer_1_competition.level_0_infra.level_1 import add_common_contest_args

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import add_model
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    add_seed_and_run_context,
)


def add_train_subparser(subparsers: Any) -> None:
    p = subparsers.add_parser("train", help="Train ARC models")
    add_common_contest_args(p)
    add_model(p, default="baseline_approx")
    add_max_targets_arg(p, default=0)
    add_seed_and_run_context(p)
