"""Candidate ranking + final chosen-params fallback for LLM-TTA DFS."""

import time
from typing import Any, Mapping

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_0_infra.level_0 import (
    ArcLmBudget,
    LlmTtaDfsConfig,
)
from layers.layer_1_competition.level_0_infra.level_1 import (
    CandidatePrediction,
    rank_candidate_grids,
)

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    coerce_arc_grid,
    empty_arc_grid_like,
    predict_attempts_from_chosen_params,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.ensemble_prediction_bridge import (
    ensemble_rank_predictions_reference,
)

logger = get_logger(__name__)

Grid = list[list[int]]


def pick_ranked_attempts(
    predictions: list[CandidatePrediction],
    config: LlmTtaDfsConfig,
    chosen_params: Mapping[str, Any] | None,
    base_input: Grid,
    started: float,
    backend_meta: dict[str, Any],
    mode: str,
    num_augmentations: int,
    budget: ArcLmBudget,
    artifact_meta: dict[str, Any],
) -> tuple[Grid, Grid, dict[str, Any]] | None:
    """Return two attempts from the configured ranker, or ``None`` if ranking is empty."""
    ranker = str(config.candidate_ranker or "default").strip().lower()
    if ranker == "default":
        ranked = rank_candidate_grids(
            predictions,
            consistency_weight=float(config.consistency_weight),
            model_weight=float(config.model_weight),
            augmentation_likelihood_weight=float(config.augmentation_likelihood_weight),
        )
        if ranked:
            a1 = coerce_arc_grid(ranked[0].grid, base_input)
            if len(ranked) > 1:
                a2 = coerce_arc_grid(ranked[1].grid, empty_arc_grid_like(base_input))
            else:
                _, fallback = predict_attempts_from_chosen_params(base_input, chosen_params)
                a2 = coerce_arc_grid(fallback, empty_arc_grid_like(base_input))
            meta_ok: dict[str, Any] = {
                "status": "ok",
                "execution_mode": mode,
                "ranked_count": len(ranked),
                "candidate_ranker": ranker,
                "augmentations": num_augmentations,
                "backend": backend_meta.get("backend"),
                "adaptation": backend_meta.get("adaptation"),
                "elapsed_sec": float(time.perf_counter() - started),
                "budget_stop_reason": budget.stop_reason,
            }
            if artifact_meta:
                meta_ok["infer_artifacts"] = artifact_meta
            return a1, a2, meta_ok
    else:
        ordered = ensemble_rank_predictions_reference(predictions, ranker=ranker)
        if ordered:
            a1 = coerce_arc_grid(ordered[0], base_input)
            if len(ordered) > 1:
                a2 = coerce_arc_grid(ordered[1], empty_arc_grid_like(base_input))
            else:
                _, fallback = predict_attempts_from_chosen_params(base_input, chosen_params)
                a2 = coerce_arc_grid(fallback, empty_arc_grid_like(base_input))
            meta_ok2: dict[str, Any] = {
                "status": "ok",
                "execution_mode": mode,
                "ranked_count": len(ordered),
                "candidate_ranker": ranker,
                "augmentations": num_augmentations,
                "backend": backend_meta.get("backend"),
                "adaptation": backend_meta.get("adaptation"),
                "elapsed_sec": float(time.perf_counter() - started),
                "budget_stop_reason": budget.stop_reason,
            }
            if artifact_meta:
                meta_ok2["infer_artifacts"] = artifact_meta
            return a1, a2, meta_ok2
    return None


def build_fallback_attempts(
    base_input: Grid,
    chosen_params: Mapping[str, Any] | None,
    started: float,
    backend_meta: dict[str, Any],
    mode: str,
    num_augmentations: int,
    budget: ArcLmBudget,
    artifact_meta: dict[str, Any],
) -> tuple[Grid, Grid, dict[str, Any]]:
    """Final chosen-params fallback when ranking produced no candidates."""
    a1, a2 = predict_attempts_from_chosen_params(base_input, chosen_params)
    logger.warning("llm_tta_dfs produced no ranked candidates; falling back to chosen_params.")
    meta_fb: dict[str, Any] = {
        "status": "fallback_no_candidates",
        "execution_mode": mode,
        "augmentations": num_augmentations,
        "backend": backend_meta.get("backend"),
        "adaptation": backend_meta.get("adaptation"),
        "elapsed_sec": float(time.perf_counter() - started),
        "budget_stop_reason": budget.stop_reason,
    }
    if artifact_meta:
        meta_fb["infer_artifacts"] = artifact_meta
    return a1, a2, meta_fb
