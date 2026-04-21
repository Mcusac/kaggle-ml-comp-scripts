"""Register the ``validate_data`` subparser."""

from typing import Any

from layers.layer_1_competition.level_0_infra.level_1 import add_common_contest_args

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    add_max_targets,
)


def add_validate_data_subparser(subparsers: Any) -> None:
    p = subparsers.add_parser("validate_data", help="Validate ARC inputs under --data-root")
    add_common_contest_args(p)
    add_max_targets(p, default=0)
