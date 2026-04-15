from typing import Any

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import add_llm_tta_args


def add_llm(parser: Any) -> None:
    add_llm_tta_args(parser)