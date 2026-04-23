"""Register the ``submit`` subparser."""

from typing import Any

from layers.layer_1_competition.level_0_infra.level_0 import (
    add_ensemble_weights_arg,
    add_llm_tta_args,
    add_max_targets_arg,
    add_output_csv_arg,
    add_validation_stacking_toggle,
)
from layers.layer_1_competition.level_0_infra.level_1 import add_common_contest_args

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    add_model,
    add_strategy,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    add_seed_and_run_context,
)


def add_submit_subparser(subparsers: Any) -> None:
    p = subparsers.add_parser("submit", help="Generate submission")
    add_common_contest_args(p)
    add_strategy(p, default="single")
    add_model(p, default="baseline_approx")
    p.add_argument("--train-mode", default="end_to_end")
    add_output_csv_arg(p)
    add_max_targets_arg(p)
    add_ensemble_weights_arg(p)
    add_validation_stacking_toggle(p)
    p.add_argument("--tuned-config", type=str, default=None)
    p.add_argument("--neural-checkpoint", type=str, default=None)
    p.add_argument("--neural-train-config", type=str, default=None)
    add_llm_tta_args(p)
    add_seed_and_run_context(p)
