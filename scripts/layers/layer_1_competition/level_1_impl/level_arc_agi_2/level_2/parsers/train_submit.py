"""Register the ``train_and_submit`` subparser."""

from typing import Any

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    add_common,
    add_ensemble,
    add_llm_tta_args,
    add_max_targets,
    add_model,
    add_output,
    add_stacking,
    add_strategy,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    add_seed_and_run_context,
)


def add_train_and_submit_subparser(subparsers: Any) -> None:
    p = subparsers.add_parser("train_and_submit", help="Train then submit")
    add_common(p)
    p.add_argument("--train-mode", default="end_to_end")
    add_model(p, default="grid_cnn_v0")
    add_strategy(p, default="single")
    add_output(p)
    add_max_targets(p)
    add_ensemble(p)
    add_stacking(p)
    add_llm_tta_args(p)
    add_seed_and_run_context(p)
