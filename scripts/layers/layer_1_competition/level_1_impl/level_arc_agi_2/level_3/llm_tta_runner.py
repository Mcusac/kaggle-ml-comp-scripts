"""LLM-TTA DFS orchestration (level_3): composes level_2 LM backends and level_1 decoders."""

from __future__ import annotations

import time
from typing import Any, Callable, Mapping

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import predict_attempts_from_chosen_params
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.augmentations import (
    apply_augmentation,
    generate_augmentation_specs,
    invert_augmentation,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.candidate_scoring import (
    CandidatePrediction,
    rank_candidate_grids,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.decoder_dfs import decode_grid_candidates
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.token_decoder import decode_tokens_to_grids
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.arc_lm_adaptation import (
    ArcLmAdaptationConfig,
    run_task_adaptation,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.arc_lm_backend import (
    ArcLmBackendConfig,
    build_lm_backend,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.arc_lm_runtime import (
    ArcLmRuntimeProfile,
    apply_runtime_profile,
    build_budget,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.ensemble_prediction_bridge import (
    ensemble_rank_predictions_reference,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.llm_tta_inference import (
    LlmTtaDfsConfig,
    _build_cell_probabilities,
    _collect_support_grids,
    _empty_like,
    _grid_shape,
    _safe_grid,
    _task_seed,
    _validate_config,
)

logger = get_logger(__name__)

Grid = list[list[int]]


def _build_runtime_profile(config: LlmTtaDfsConfig) -> ArcLmRuntimeProfile:
    return ArcLmRuntimeProfile(
        attention_mode=str(config.runtime_attention_mode or "auto"),
        disable_compile=bool(config.runtime_disable_compile),
        allocator_expandable_segments=bool(config.runtime_allocator_expandable_segments),
        allocator_max_split_size_mb=int(config.runtime_allocator_max_split_size_mb or 0),
    )


def _build_backend_probs(
    base_input: Grid,
    config: LlmTtaDfsConfig,
    task_payload: Mapping[str, Any] | None,
    budget_expired: Callable[[], bool],
) -> tuple[list[list[list[float]]] | None, dict[str, Any], Any]:
    backend_cfg = ArcLmBackendConfig(
        model_path=str(config.model_path),
        lora_path=config.lora_path,
        attention_mode=str(config.runtime_attention_mode or "auto"),
        disable_compile=bool(config.runtime_disable_compile),
        seed=int(config.seed or 0),
    )
    backend = build_lm_backend(backend_cfg)
    backend.load()
    adapt_cfg = ArcLmAdaptationConfig(
        steps=int(config.adapt_steps or 0),
        batch_size=max(1, int(config.adapt_batch_size or 1)),
        gradient_accumulation_steps=max(1, int(config.adapt_gradient_accumulation_steps or 1)),
        disabled=bool(config.adapt_disabled),
    )
    adapt_meta = run_task_adaptation(
        backend=backend,
        task_payload=task_payload if isinstance(task_payload, dict) else {},
        cfg=adapt_cfg,
        budget_expired=budget_expired,
    )
    return backend.infer_cell_probs(base_input), {
        "backend": backend.backend_name(),
        "adaptation": adapt_meta,
    }, backend


def predict_attempts_for_llm_tta_dfs(
    input_grid: Grid,
    *,
    task_payload: Mapping[str, Any] | None,
    task_id: str,
    test_index: int,
    chosen_params: Mapping[str, Any] | None,
    config: LlmTtaDfsConfig,
) -> tuple[Grid, Grid, dict[str, Any]]:
    """Produce two ARC attempts using surrogate or LM-backed constrained decoding."""
    _validate_config(config)
    started = float(time.perf_counter())
    apply_runtime_profile(_build_runtime_profile(config))
    budget = build_budget(
        max_runtime_sec=float(config.max_runtime_sec or 0.0),
        task_runtime_sec=float(config.task_runtime_sec or 0.0),
        decode_runtime_sec=float(config.decode_runtime_sec or 0.0),
    )

    base_input = _safe_grid(input_grid, input_grid)
    h, w = _grid_shape(base_input)
    if h <= 0 or w <= 0:
        return [], [], {"status": "empty_input"}
    if budget.is_expired():
        a1, a2 = predict_attempts_from_chosen_params(base_input, chosen_params)
        return a1, a2, {"status": "fallback_budget", "reason": budget.stop_reason}

    mode = str(config.execution_mode or "surrogate").strip().lower()
    backend_meta: dict[str, Any] = {"backend": "surrogate", "adaptation": {"status": "not_applicable"}}
    lm_probs: list[list[list[float]]] | None = None
    lm_backend: Any = None
    if mode == "lm_backend":
        lm_probs, backend_meta, lm_backend = _build_backend_probs(base_input, config, task_payload, budget.is_expired)

    specs = generate_augmentation_specs(
        int(config.num_augmentations or 1),
        seed=_task_seed(task_id, test_index, int(config.seed or 0)),
        include_identity=True,
    )
    predictions: list[CandidatePrediction] = []
    for i, spec in enumerate(specs):
        if budget.is_expired():
            break
        aug_input = apply_augmentation(base_input, spec)
        ah, aw = _grid_shape(aug_input)
        if lm_probs is not None:
            probs = lm_probs
            decoded = decode_tokens_to_grids(
                input_grid=aug_input,
                token_probs_provider=lambda _prefix: {i: probs[min(len(_prefix) // max(1, aw), ah - 1)][len(_prefix) % max(1, aw)][i] for i in range(10)},
                beam_width=int(config.beam_width or 1),
                max_candidates=int(config.max_candidates or 1),
                max_neg_log_score=float(config.max_neg_log_score or 120.0),
            )
            decoded = [type("Tmp", (), {"grid": cand.grid, "score": cand.score}) for cand in decoded]
        else:
            raw_support = _collect_support_grids(task_payload, base_input)
            support = [apply_augmentation(sg, spec) for sg in raw_support]
            if not support:
                support = [aug_input]
            probs = _build_cell_probabilities(support, ah, aw)
            decoded = decode_grid_candidates(
                probs,
                beam_width=int(config.beam_width or 1),
                max_candidates=int(config.max_candidates or 1),
                max_neg_log_score=float(config.max_neg_log_score or 120.0),
            )
        for cand in decoded:
            inv_grid = invert_augmentation(cand.grid, spec)
            aug_likelihood = 0.0
            if lm_probs is not None and isinstance(task_payload, Mapping) and lm_backend is not None:
                try:
                    aug_likelihood = float(
                        lm_backend.score_candidate_grid(task_payload if isinstance(task_payload, dict) else {}, inv_grid)
                    )
                except Exception as e:
                    logger.warning("LM candidate scoring failed; using decode score only: %s", e)
            predictions.append(
                CandidatePrediction(
                    grid=inv_grid,
                    model_score=float(cand.score),
                    aug_key=f"aug_{i}",
                    aug_likelihood_score=float(aug_likelihood),
                )
            )

    ranker = str(config.candidate_ranker or "default").strip().lower()
    if ranker == "default":
        ranked = rank_candidate_grids(
            predictions,
            consistency_weight=float(config.consistency_weight),
            model_weight=float(config.model_weight),
            augmentation_likelihood_weight=float(config.augmentation_likelihood_weight),
        )
        if ranked:
            a1 = _safe_grid(ranked[0].grid, base_input)
            if len(ranked) > 1:
                a2 = _safe_grid(ranked[1].grid, _empty_like(base_input))
            else:
                _, fallback = predict_attempts_from_chosen_params(base_input, chosen_params)
                a2 = _safe_grid(fallback, _empty_like(base_input))
            return a1, a2, {
                "status": "ok",
                "execution_mode": mode,
                "ranked_count": len(ranked),
                "candidate_ranker": ranker,
                "augmentations": len(specs),
                "backend": backend_meta.get("backend"),
                "adaptation": backend_meta.get("adaptation"),
                "elapsed_sec": float(time.perf_counter() - started),
                "budget_stop_reason": budget.stop_reason,
            }
    else:
        ordered = ensemble_rank_predictions_reference(predictions, ranker=ranker)
        if ordered:
            a1 = _safe_grid(ordered[0], base_input)
            if len(ordered) > 1:
                a2 = _safe_grid(ordered[1], _empty_like(base_input))
            else:
                _, fallback = predict_attempts_from_chosen_params(base_input, chosen_params)
                a2 = _safe_grid(fallback, _empty_like(base_input))
            return a1, a2, {
                "status": "ok",
                "execution_mode": mode,
                "ranked_count": len(ordered),
                "candidate_ranker": ranker,
                "augmentations": len(specs),
                "backend": backend_meta.get("backend"),
                "adaptation": backend_meta.get("adaptation"),
                "elapsed_sec": float(time.perf_counter() - started),
                "budget_stop_reason": budget.stop_reason,
            }

    a1, a2 = predict_attempts_from_chosen_params(base_input, chosen_params)
    logger.warning("llm_tta_dfs produced no ranked candidates; falling back to chosen_params.")
    return a1, a2, {
        "status": "fallback_no_candidates",
        "execution_mode": mode,
        "augmentations": len(specs),
        "backend": backend_meta.get("backend"),
        "adaptation": backend_meta.get("adaptation"),
        "elapsed_sec": float(time.perf_counter() - started),
        "budget_stop_reason": budget.stop_reason,
    }
