"""Register the ``tune_and_submit`` subparser."""

from typing import Any

from layers.layer_1_competition.level_0_infra.level_0 import add_llm_tta_args
from layers.layer_1_competition.level_0_infra.level_1 import add_common_contest_args

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    add_ensemble,
    add_max_targets,
    add_model,
    add_output,
    add_search_type,
    add_stacking,
    add_strategy,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    add_seed_and_run_context,
)


def add_tune_and_submit_subparser(subparsers: Any) -> None:
    p = subparsers.add_parser("tune_and_submit", help="Tune then submit")
    add_common_contest_args(p)
    add_search_type(p, default="quick")
    add_model(p, default="baseline_approx")
    add_strategy(p, default="single")
    add_output(p)
    add_max_targets(p)
    add_ensemble(p)
    add_stacking(p)
    add_llm_tta_args(p)
    add_seed_and_run_context(p)
