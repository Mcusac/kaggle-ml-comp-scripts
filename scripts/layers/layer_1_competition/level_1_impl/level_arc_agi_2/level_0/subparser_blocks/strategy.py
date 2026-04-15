from typing import Any
from layers.layer_1_competition.level_0_infra.level_1 import add_strategy_arg


STRATEGY_CHOICES = (
    "single",
    "ensemble",
    "llm_tta_dfs",
    "stacking",
    "stacking_ensemble",
)


def add_strategy(parser: Any, default: str = "single") -> None:
    """
    Submission / inference strategy selector.
    """
    add_strategy_arg(
        parser,
        choices=STRATEGY_CHOICES,
        default=default,
        help_text="ARC execution strategy",
    )