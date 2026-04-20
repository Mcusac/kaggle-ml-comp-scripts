"""Thin LLM-TTA DFS orchestrator.

Composes budget/profile helpers, the LM backend session, three decode branches,
artifact IO, and ranking/fallback selection. Per-augmentation candidates are
accumulated in a single ``predictions`` list and then ranked once at the end.
"""

import time
from typing import Any, Mapping

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    LlmTtaDfsConfig,
    apply_augmentation,
    apply_runtime_profile,
    build_budget,
    coerce_arc_grid,
    generate_augmentation_specs,
    invert_augmentation,
    llm_tta_augment_seed,
    llm_tta_grid_hw,
    predict_attempts_from_chosen_params,
    validate_llm_tta_dfs_config,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    CandidatePrediction,
)

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3 import (
    prepare_artifact_layout,
    write_decoded_shard,
    write_intermediate_candidates,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3 import (
    build_fallback_attempts,
    pick_ranked_attempts,
    build_runtime_profile,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_4 import (
    build_lm_backend,
    restore_adapter_safely,
    decode_with_cell_probs,
    decode_with_support_grids,
    decode_with_turbo_lm,
)


logger = get_logger(__name__)

Grid = list[list[int]]


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
    validate_llm_tta_dfs_config(config)
    started = float(time.perf_counter())
    apply_runtime_profile(build_runtime_profile(config))
    budget = build_budget(
        max_runtime_sec=float(config.max_runtime_sec or 0.0),
        task_runtime_sec=float(config.task_runtime_sec or 0.0),
        decode_runtime_sec=float(config.decode_runtime_sec or 0.0),
    )

    base_input = coerce_arc_grid(input_grid, input_grid)
    h, w = llm_tta_grid_hw(base_input)
    if h <= 0 or w <= 0:
        return [], [], {"status": "empty_input"}
    if budget.is_expired():
        a1, a2 = predict_attempts_from_chosen_params(base_input, chosen_params)
        return a1, a2, {"status": "fallback_budget", "reason": budget.stop_reason}

    lm_backend: Any | None = None
    try:
        mode = str(config.execution_mode or "surrogate").strip().lower()
        backend_meta: dict[str, Any] = {"backend": "surrogate", "adaptation": {"status": "not_applicable"}}
        lm_probs: list[list[list[float]]] | None = None
        use_turbo_lm: bool = False
        if mode == "lm_backend":
            backend_meta, lm_backend = build_lm_backend(config, task_payload, budget.is_expired)
            tok = lm_backend.get_tokenizer()
            use_turbo_lm = tok is not None
            if not use_turbo_lm:
                lm_probs = lm_backend.infer_cell_probs(base_input)

        specs = generate_augmentation_specs(
            int(config.num_augmentations or 1),
            seed=llm_tta_augment_seed(task_id, test_index, int(config.seed or 0)),
            include_identity=True,
        )
        infer_out, inter_dir, basekey, artifact_meta = prepare_artifact_layout(
            config, str(task_id), int(test_index)
        )

        predictions: list[CandidatePrediction] = []
        for i, spec in enumerate(specs):
            if budget.is_expired():
                break
            aug_input = apply_augmentation(base_input, spec)
            ah, aw = llm_tta_grid_hw(aug_input)
            if lm_probs is not None:
                decoded = decode_with_cell_probs(aug_input, lm_probs, ah, aw, config)
            elif use_turbo_lm and lm_backend is not None:
                decoded = decode_with_turbo_lm(aug_input, lm_backend, config, budget)
            else:
                decoded = decode_with_support_grids(
                    aug_input, base_input, spec, task_payload, ah, aw, config
                )
            shard: list[dict[str, Any]] = []
            for cand in decoded:
                inv_grid = invert_augmentation(cand.grid, spec)
                aug_likelihood = 0.0
                if (lm_probs is not None or use_turbo_lm) and isinstance(task_payload, Mapping) and lm_backend is not None:
                    try:
                        aug_likelihood = float(
                            lm_backend.score_candidate_grid(
                                task_payload if isinstance(task_payload, dict) else {}, inv_grid
                            )
                        )
                    except Exception as e:
                        logger.warning("LM candidate scoring failed; using decode score only: %s", e)
                if infer_out:
                    shard.append(
                        {
                            "solution": [list(row) for row in inv_grid],
                            "beam_score": float(-float(cand.score)),
                            "score_aug": [float(aug_likelihood)],
                        }
                    )
                predictions.append(
                    CandidatePrediction(
                        grid=inv_grid,
                        model_score=float(cand.score),
                        aug_key=f"aug_{i}",
                        aug_likelihood_score=float(aug_likelihood),
                    )
                )
            if infer_out:
                write_decoded_shard(infer_out, basekey, i, shard)

        if inter_dir:
            write_intermediate_candidates(
                inter_dir, basekey, str(task_id), int(test_index), mode, config, predictions
            )

        picked = pick_ranked_attempts(
            predictions,
            config,
            chosen_params,
            base_input,
            started,
            backend_meta,
            mode,
            len(specs),
            budget,
            artifact_meta,
        )
        if picked is not None:
            return picked

        return build_fallback_attempts(
            base_input,
            chosen_params,
            started,
            backend_meta,
            mode,
            len(specs),
            budget,
            artifact_meta,
        )
    finally:
        restore_adapter_safely(lm_backend)
