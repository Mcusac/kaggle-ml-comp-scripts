"""Submit-strategy dispatch: produces two attempt grids for a given strategy.

Supports ``single`` (use chosen_params directly) and ``ensemble`` (rank
heuristics on training data and pick the top two). Stacking strategies are
not implemented for ARC and raise explicitly.

Intra-package dependencies (fully qualified per architecture rules):
  layers...level_arc_agi_2.level_1.heuristics     — predict_attempts_for_heuristic,
                                                      predict_attempts_from_chosen_params,
                                                      heuristic_order_for_train_mode
  layers...level_arc_agi_2.level_1.scoring         — rank_heuristics_on_training
  layers...level_arc_agi_2.level_1.submit_limits   — read_submit_max_tasks_env
"""

from typing import Any, Mapping

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    heuristic_order_for_train_mode,
    predict_attempts_for_heuristic,
    predict_attempts_from_chosen_params,
    read_submit_max_tasks_env,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    rank_heuristics_on_training,
)

logger = get_logger(__name__)


def predict_attempts_for_submit_strategy(
    input_grid: list[list[int]],
    *,
    strategy: str,
    chosen_params: Mapping[str, Any] | None,
    data_root: str | None,
    train_mode: str = "end_to_end",
    max_pairs_per_task: int = 0,
) -> tuple[list[list[int]], list[list[int]]]:
    """Produce two attempt grids for ``single`` or ``ensemble`` strategy.

    Raises ``ValueError`` for stacking strategies (not implemented for ARC,
    which has no validation predictions).
    """
    s = str(strategy or "").strip().lower()
    if s in ("stacking", "stacking_ensemble"):
        raise ValueError(
            f"Strategy {strategy!r} is not implemented for ARC (requires validation predictions). "
            "Use single or ensemble."
        )
    if s == "single":
        return predict_attempts_from_chosen_params(input_grid, chosen_params)
    if s != "ensemble":
        logger.warning("Unknown strategy %r; using single", strategy)
        return predict_attempts_from_chosen_params(input_grid, chosen_params)

    # ensemble: rank heuristics on training data and pick the top two
    if not data_root or not str(data_root).strip():
        logger.warning("ensemble requested without data_root; falling back to single")
        return predict_attempts_from_chosen_params(input_grid, chosen_params)

    order = heuristic_order_for_train_mode(train_mode)
    ranked = rank_heuristics_on_training(
        str(data_root).strip(),
        order,
        max_tasks=read_submit_max_tasks_env() or 0,
        max_pairs_per_task=int(max_pairs_per_task or 0),
    )
    if not ranked:
        return predict_attempts_from_chosen_params(input_grid, chosen_params)

    h1 = ranked[0][0]
    h2 = ranked[1][0] if len(ranked) > 1 else h1
    a1, _ = predict_attempts_for_heuristic(input_grid, h1)
    a2, _ = predict_attempts_for_heuristic(input_grid, h2)
    return a1, a2