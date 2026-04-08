"""LLM-TTA DFS orchestration (level_3): composes level_2 LM backends and level_1 decoders."""

import os
import time

from typing import Any, Callable, Mapping

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    ArcLmAdaptationConfig,
    ArcLmBudget,
    ArcLmRuntimeProfile,
    CandidatePrediction,
    LlmTtaDfsConfig,
    apply_augmentation,
    apply_runtime_profile,
    build_budget,
    build_cell_probs_from_support_grids,
    collect_llm_tta_support_grids,
    coerce_arc_grid,
    decode_grid_candidates,
    decode_tokens_to_grids,
    empty_arc_grid_like,
    generate_augmentation_specs,
    infer_ensure_run_layout,
    infer_eval_basekey,
    infer_save_decoded_result_shard,
    infer_save_intermediate_candidates,
    infer_shard_basename,
    invert_augmentation,
    llm_tta_augment_seed,
    llm_tta_grid_hw,
    predict_attempts_from_chosen_params,
    rank_candidate_grids,
    run_task_adaptation,
    validate_llm_tta_dfs_config,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    ArcQwenGridChatFormatter,
    ensemble_rank_predictions_reference,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2 import (
    ArcLmBackendConfig,
    build_lm_backend,
)

logger = get_logger(__name__)

Grid = list[list[int]]


def _turbo_wall_end_time(budget: ArcLmBudget) -> float:
    """Map perf_counter deadlines in ``ArcLmBudget`` to ``time.time()`` for ``inference_turbo_dfs``."""
    now_pc = budget.now()
    remain: list[float] = []
    if budget.global_deadline_ts > 0.0:
        remain.append(float(budget.global_deadline_ts - now_pc))
    if budget.task_deadline_ts > 0.0:
        remain.append(float(budget.task_deadline_ts - now_pc))
    if budget.decode_deadline_ts > 0.0:
        remain.append(float(budget.decode_deadline_ts - now_pc))
    if not remain:
        return float(time.time()) + 86400.0
    return float(time.time()) + max(0.0, min(remain))


def _build_runtime_profile(config: LlmTtaDfsConfig) -> ArcLmRuntimeProfile:
    return ArcLmRuntimeProfile(
        attention_mode=str(config.runtime_attention_mode or "auto"),
        disable_compile=bool(config.runtime_disable_compile),
        allocator_expandable_segments=bool(config.runtime_allocator_expandable_segments),
        allocator_max_split_size_mb=int(config.runtime_allocator_max_split_size_mb or 0),
    )


def _per_task_adaptation_should_run(config: LlmTtaDfsConfig) -> bool:
    """NVARC-style fine-tune before decode when ``per_task_adaptation`` is on (explicit opt-in)."""
    if not bool(getattr(config, "per_task_adaptation", False)):
        return False
    if bool(config.adapt_disabled):
        return False
    return int(config.adapt_steps or 0) > 0


def _build_lm_backend(
    config: LlmTtaDfsConfig,
    task_payload: Mapping[str, Any] | None,
    budget_expired: Callable[[], bool],
) -> tuple[dict[str, Any], Any]:
    backend_cfg = ArcLmBackendConfig(
        model_path=str(config.model_path),
        lora_path=config.lora_path,
        attention_mode=str(config.runtime_attention_mode or "auto"),
        disable_compile=bool(config.runtime_disable_compile),
        seed=int(config.seed or 0),
    )
    backend = build_lm_backend(backend_cfg)
    backend.load()
    if _per_task_adaptation_should_run(config):
        adapt_cfg = ArcLmAdaptationConfig(
            steps=int(config.adapt_steps or 0),
            batch_size=max(1, int(config.adapt_batch_size or 1)),
            gradient_accumulation_steps=max(1, int(config.adapt_gradient_accumulation_steps or 1)),
            disabled=False,
        )
        adapt_meta = run_task_adaptation(
            backend=backend,
            task_payload=task_payload if isinstance(task_payload, dict) else {},
            cfg=adapt_cfg,
            budget_expired=budget_expired,
        )
    else:
        adapt_meta = {"status": "skipped", "reason": "per_task_adaptation_off", "steps_ran": 0}
    return {
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
    validate_llm_tta_dfs_config(config)
    started = float(time.perf_counter())
    apply_runtime_profile(_build_runtime_profile(config))
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
            backend_meta, lm_backend = _build_lm_backend(config, task_payload, budget.is_expired)
            tok = lm_backend.get_tokenizer()
            use_turbo_lm = tok is not None
            if not use_turbo_lm:
                lm_probs = lm_backend.infer_cell_probs(base_input)

        specs = generate_augmentation_specs(
            int(config.num_augmentations or 1),
            seed=llm_tta_augment_seed(task_id, test_index, int(config.seed or 0)),
            include_identity=True,
        )
        artifact_root = str(getattr(config, "infer_artifact_dir", None) or "").strip()
        infer_out: str | None = None
        inter_dir: str | None = None
        basekey = infer_eval_basekey(str(task_id), int(test_index))
        artifact_meta: dict[str, Any] = {}
        if artifact_root:
            infer_out, _, inter_dir = infer_ensure_run_layout(artifact_root)
            artifact_meta = {
                "infer_artifact_dir": artifact_root,
                "inference_outputs_dir": infer_out,
                "intermediate_candidates_dir": inter_dir,
                "infer_artifact_run_name": str(getattr(config, "infer_artifact_run_name", "") or ""),
                "basekey": basekey,
            }
        predictions: list[CandidatePrediction] = []
        for i, spec in enumerate(specs):
            if budget.is_expired():
                break
            aug_input = apply_augmentation(base_input, spec)
            ah, aw = llm_tta_grid_hw(aug_input)
            if lm_probs is not None:
                probs = lm_probs
                decoded = decode_tokens_to_grids(
                    input_grid=aug_input,
                    token_probs_provider=lambda _prefix: {
                        i: probs[min(len(_prefix) // max(1, aw), ah - 1)][len(_prefix) % max(1, aw)][i]
                        for i in range(10)
                    },
                    beam_width=int(config.beam_width or 1),
                    max_candidates=int(config.max_candidates or 1),
                    max_neg_log_score=float(config.max_neg_log_score or 120.0),
                )
                decoded = [type("Tmp", (), {"grid": cand.grid, "score": cand.score}) for cand in decoded]
            elif use_turbo_lm and lm_backend is not None:
                tok = lm_backend.get_tokenizer()
                fmt = ArcQwenGridChatFormatter(tokenizer=tok)
                prompt = fmt.fmt_query_from_input_grid(aug_input)
                raw_ids = tok.encode(prompt, add_special_tokens=False)
                if hasattr(raw_ids, "tolist"):
                    prefix_ids = [int(x) for x in raw_ids.tolist()]
                elif isinstance(raw_ids, list):
                    prefix_ids = [int(x) for x in raw_ids]
                else:
                    prefix_ids = [int(x) for x in list(raw_ids)]
                max_nt = (
                    int(config.turbo_max_new_tokens)
                    if config.turbo_max_new_tokens is not None
                    else int(fmt.max_new_tokens_for_max_grid() + 1)
                )
                end_wall = _turbo_wall_end_time(budget)
                beams = lm_backend.turbo_dfs_beams(
                    list(prefix_ids),
                    max_nt,
                    float(config.turbo_prune_max_nll),
                    end_wall,
                    inner_loop_wall_sec=config.turbo_inner_loop_wall_sec,
                )
                mc = max(1, int(config.max_candidates or 1))
                decoded = []
                for nll, suffix in beams[:mc]:
                    full_ids = list(prefix_ids) + list(suffix)
                    grid = fmt.decode_tokens_to_grid(full_ids)
                    if grid is None:
                        continue
                    decoded.append(type("Tmp", (), {"grid": grid, "score": float(-nll)})())
            else:
                raw_support = collect_llm_tta_support_grids(task_payload, base_input)
                support = [apply_augmentation(sg, spec) for sg in raw_support]
                if not support:
                    support = [aug_input]
                probs = build_cell_probs_from_support_grids(support, ah, aw)
                decoded = decode_grid_candidates(
                    probs,
                    beam_width=int(config.beam_width or 1),
                    max_candidates=int(config.max_candidates or 1),
                    max_neg_log_score=float(config.max_neg_log_score or 120.0),
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
            if infer_out and shard:
                shard_path = os.path.join(infer_out, infer_shard_basename(basekey, i))
                try:
                    infer_save_decoded_result_shard(shard_path, shard)
                except Exception as e:
                    logger.warning("⚠️ inference_outputs shard write failed (%s): %s", shard_path, e)

        if inter_dir:
            try:
                infer_save_intermediate_candidates(
                    os.path.join(inter_dir, f"{basekey}.json"),
                    {
                        "task_id": str(task_id),
                        "test_index": int(test_index),
                        "basekey": basekey,
                        "execution_mode": mode,
                        "candidate_ranker": str(config.candidate_ranker or "default"),
                        "candidates": [
                            {
                                "aug_key": p.aug_key,
                                "model_score": float(p.model_score),
                                "aug_likelihood_score": float(p.aug_likelihood_score),
                                "grid": [list(row) for row in p.grid],
                            }
                            for p in predictions
                        ],
                    },
                )
            except Exception as e:
                logger.warning("⚠️ intermediate_candidates write failed: %s", e)

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
                    "augmentations": len(specs),
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
                    "augmentations": len(specs),
                    "backend": backend_meta.get("backend"),
                    "adaptation": backend_meta.get("adaptation"),
                    "elapsed_sec": float(time.perf_counter() - started),
                    "budget_stop_reason": budget.stop_reason,
                }
                if artifact_meta:
                    meta_ok2["infer_artifacts"] = artifact_meta
                return a1, a2, meta_ok2

        a1, a2 = predict_attempts_from_chosen_params(base_input, chosen_params)
        logger.warning("llm_tta_dfs produced no ranked candidates; falling back to chosen_params.")
        meta_fb: dict[str, Any] = {
            "status": "fallback_no_candidates",
            "execution_mode": mode,
            "augmentations": len(specs),
            "backend": backend_meta.get("backend"),
            "adaptation": backend_meta.get("adaptation"),
            "elapsed_sec": float(time.perf_counter() - started),
            "budget_stop_reason": budget.stop_reason,
        }
        if artifact_meta:
            meta_fb["infer_artifacts"] = artifact_meta
        return a1, a2, meta_fb
    finally:
        if lm_backend is not None:
            try:
                lm_backend.restore_base_adapter_after_task()
            except Exception as e:
                logger.warning("⚠️ restore_base_adapter_after_task failed (task-scoped cleanup): %s", e)
