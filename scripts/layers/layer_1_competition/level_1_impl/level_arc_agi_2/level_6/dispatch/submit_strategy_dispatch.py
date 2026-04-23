"""Submit-strategy dispatch: wires heuristics, scoring, and optional LLM-TTA."""

from typing import Any, Mapping

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_0_infra.level_0 import LlmTtaDfsConfig

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    predict_attempts_from_chosen_params,
    stack_raise_if_unsupported_strategy,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_5 import (
    predict_attempts_for_llm_tta_dfs,
)

_logger = get_logger(__name__)


def predict_attempts_for_submit_strategy(
    input_grid: list[list[int]],
    *,
    strategy: str,
    chosen_params: Mapping[str, Any] | None,
    data_root: str | None,
    train_mode: str = "end_to_end",
    max_pairs_per_task: int = 0,
    task_payload: Mapping[str, Any] | None = None,
    task_id: str = "",
    test_index: int = 0,
    llm_tta_config: LlmTtaDfsConfig | None = None,
    return_metadata: bool = False,
) -> tuple[list[list[int]], list[list[int]]] | tuple[list[list[int]], list[list[int]], dict[str, Any]]:
    """Produce two attempt grids for ``single``, ``ensemble``, or ``llm_tta_dfs`` strategy.

    Raises ``ValueError`` for stacking strategies (not implemented for ARC).
    """
    stack_raise_if_unsupported_strategy(strategy)
    s = str(strategy or "").strip().lower()
    if s == "llm_tta_dfs":
        cfg = llm_tta_config or LlmTtaDfsConfig()
        a1, a2, meta = predict_attempts_for_llm_tta_dfs(
            input_grid,
            task_payload=task_payload,
            task_id=task_id,
            test_index=int(test_index or 0),
            chosen_params=chosen_params,
            config=cfg,
        )
        if return_metadata:
            return a1, a2, dict(meta)
        return a1, a2
    if s == "single":
        a1, a2 = predict_attempts_from_chosen_params(input_grid, chosen_params)
        if return_metadata:
            return a1, a2, {"status": "ok", "execution_mode": "heuristic_single"}
        return a1, a2
    if s == "ensemble":
        _logger.warning(
            "ensemble strategy is not implemented (Run 12 removed the broken "
            "heuristic ranker cascade); falling back to single"
        )
        a1, a2 = predict_attempts_from_chosen_params(input_grid, chosen_params)
        if return_metadata:
            return a1, a2, {"status": "fallback_ensemble_removed", "execution_mode": "heuristic_single"}
        return a1, a2
    _logger.warning("Unknown strategy %r; using single", strategy)
    a1, a2 = predict_attempts_from_chosen_params(input_grid, chosen_params)
    if return_metadata:
        return a1, a2, {"status": "fallback_unknown_strategy", "execution_mode": "heuristic_single"}
    return a1, a2
