from typing import Any

from layers.layer_1_competition.level_0_infra.level_1 import add_common_contest_args


def add_common(parser: Any) -> None:
    add_common_contest_args(parser)