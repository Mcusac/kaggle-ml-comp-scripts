"""Submit-strategy dispatch (level_3): wires level_0 heuristics, level_1 scoring, level_2 LLM TTA."""

from __future__ import annotations

from typing import Any, Mapping

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    heuristic_order_for_train_mode,
    predict_attempts_for_heuristic,
    predict_attempts_from_chosen_params,
    read_submit_max_tasks_env,
    stack_raise_if_unsupported_strategy,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    rank_heuristics_on_training,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.llm_tta_inference import LlmTtaDfsConfig
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3.llm_tta_runner import (
    predict_attempts_for_llm_tta_dfs,
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
    if s != "ensemble":
        logger.warning("Unknown strategy %r; using single", strategy)
        a1, a2 = predict_attempts_from_chosen_params(input_grid, chosen_params)
        if return_metadata:
            return a1, a2, {"status": "fallback_unknown_strategy", "execution_mode": "heuristic_single"}
        return a1, a2

    if not data_root or not str(data_root).strip():
        logger.warning("ensemble requested without data_root; falling back to single")
        a1, a2 = predict_attempts_from_chosen_params(input_grid, chosen_params)
        if return_metadata:
            return a1, a2, {"status": "fallback_missing_data_root", "execution_mode": "heuristic_single"}
        return a1, a2

    order = heuristic_order_for_train_mode(train_mode)
    ranked = rank_heuristics_on_training(
        str(data_root).strip(),
        order,
        max_tasks=read_submit_max_tasks_env() or 0,
        max_pairs_per_task=int(max_pairs_per_task or 0),
    )
    if not ranked:
        a1, a2 = predict_attempts_from_chosen_params(input_grid, chosen_params)
        if return_metadata:
            return a1, a2, {"status": "fallback_no_ranked", "execution_mode": "heuristic_single"}
        return a1, a2

    h1 = ranked[0][0]
    h2 = ranked[1][0] if len(ranked) > 1 else h1
    a1, _ = predict_attempts_for_heuristic(input_grid, h1)
    a2, _ = predict_attempts_for_heuristic(input_grid, h2)
    if return_metadata:
        return a1, a2, {
            "status": "ok",
            "execution_mode": "heuristic_ensemble",
            "top_heuristics": [str(h1), str(h2)],
        }
    return a1, a2
