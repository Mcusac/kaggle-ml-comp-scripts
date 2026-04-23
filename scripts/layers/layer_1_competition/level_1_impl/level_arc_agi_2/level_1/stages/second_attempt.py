"""Second-attempt grid helper used by the submit stage's neural branch."""

from typing import Any

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    predict_attempts_from_chosen_params,
)

_logger = get_logger(__name__)


def second_attempt_grid(
    input_grid: list[list[int]],
    *,
    strategy: str,
    chosen_params: dict[str, Any] | None,
    data_root: str,
    train_mode: str,
    max_pairs_per_task: int,
) -> list[list[int]]:
    s = str(strategy or "").lower()
    if s == "ensemble":
        _logger.warning(
            "ensemble strategy is not implemented (Run 12 removed the broken "
            "heuristic ranker cascade); falling back to single"
        )
    _, a2 = predict_attempts_from_chosen_params(input_grid, chosen_params)
    return a2
