"""Register the ``tune`` subparser."""

from typing import Any

from layers.layer_1_competition.level_0_infra.level_0 import add_max_targets_arg
from layers.layer_1_competition.level_0_infra.level_1 import add_common_contest_args

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import add_search_type
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    add_seed_and_run_context,
)


def add_tune_subparser(subparsers: Any) -> None:
    p = subparsers.add_parser("tune", help="Tune ARC heuristic")
    add_common_contest_args(p)
    add_search_type(p, default="quick")
    add_max_targets_arg(p)
    add_seed_and_run_context(p)
