"""Register the ``submit`` subparser."""

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


def add_submit_subparser(subparsers: Any) -> None:
    p = subparsers.add_parser("submit", help="Generate submission")
    add_common(p)
    add_strategy(p, default="single")
    add_model(p, default="baseline_approx")
    p.add_argument("--train-mode", default="end_to_end")
    add_output(p)
    add_max_targets(p)
    add_ensemble(p)
    add_stacking(p)
    p.add_argument("--tuned-config", type=str, default=None)
    p.add_argument("--neural-checkpoint", type=str, default=None)
    p.add_argument("--neural-train-config", type=str, default=None)
    add_llm_tta_args(p)
    add_seed_and_run_context(p)
