"""ARC contest handlers."""

import argparse

from typing import Callable

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_0_infra.level_1 import (
    parse_models_csv,
    resolve_data_root_from_args,
    PipelineResult,
)

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    init_run_context,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2 import (
    pipeline_run_benchmark_rankers_from_artifacts,
    pipeline_run_score_submission,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_6 import (
    run_submission_pipeline_result,
    run_train_and_submit_pipeline_result,
    run_train_pipeline_result,
    run_tune_and_submit_pipeline_result,
    run_tune_pipeline_result,
    run_validate_data_pipeline,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_7 import validate_arc_optional_args

logger = get_logger(__name__)

FRAMEWORK_SUBPARSER_NAMES_TO_SKIP = frozenset({"train", "submit"})


def validate_data(args: argparse.Namespace) -> None:
    result = run_validate_data_pipeline(
        data_root=resolve_data_root_from_args(args),
        max_targets=int(getattr(args, "max_targets", 0) or 0),
        run_ctx=None,
    )
    _log_result(result)


def train(args: argparse.Namespace) -> None:
    run = init_run_context(
        stage="train",
        data_root=resolve_data_root_from_args(args),
        seed=int(getattr(args, "seed", 42)),
        run_id=getattr(args, "run_id", None),
        run_dir=getattr(args, "run_dir", None),
    )
    result = run_train_pipeline_result(
        data_root=resolve_data_root_from_args(args),
        train_mode=str(getattr(args, "train_mode", "end_to_end")),
        models=parse_models_csv(getattr(args, "models", None)),
        max_targets=int(getattr(args, "max_targets", 0) or 0),
        run_ctx=run,
    )
    _log_result(result)


def tune(args: argparse.Namespace) -> None:
    run = init_run_context(
        stage="tune",
        data_root=resolve_data_root_from_args(args),
        seed=int(getattr(args, "seed", 42)),
        run_id=getattr(args, "run_id", None),
        run_dir=getattr(args, "run_dir", None),
    )
    result = run_tune_pipeline_result(
        data_root=resolve_data_root_from_args(args),
        model_name=str(getattr(args, "model", "baseline_approx")),
        search_type=str(getattr(args, "search_type", "quick")),
        max_targets=int(getattr(args, "max_targets", 0) or 0),
        run_ctx=run,
    )
    _log_result(result)


def submit(args: argparse.Namespace) -> None:
    validate_arc_optional_args(args)
    run = init_run_context(
        stage="submit",
        data_root=resolve_data_root_from_args(args),
        seed=int(getattr(args, "seed", 42)),
        run_id=getattr(args, "run_id", None),
        run_dir=getattr(args, "run_dir", None),
    )
    result = run_submission_pipeline_result(
        data_root=resolve_data_root_from_args(args),
        strategy=str(getattr(args, "strategy", "single")),
        output_json=getattr(args, "output_csv", None),
        max_targets=int(getattr(args, "max_targets", 0) or 0),
        run_ctx=run,
        tuned_config_path=getattr(args, "tuned_config", None),
        models=parse_models_csv(getattr(args, "models", None)),
        neural_checkpoint_path=getattr(args, "neural_checkpoint", None),
        neural_train_config_path=getattr(args, "neural_train_config", None),
        train_mode=str(getattr(args, "train_mode", "end_to_end")),
        llm_execution_mode=str(getattr(args, "llm_execution_mode", "surrogate") or "surrogate"),
        llm_num_augmentations=int(getattr(args, "llm_num_augmentations", 8) or 8),
        llm_beam_width=int(getattr(args, "llm_beam_width", 12) or 12),
        llm_max_candidates=int(getattr(args, "llm_max_candidates", 6) or 6),
        llm_max_neg_log_score=float(getattr(args, "llm_max_neg_log_score", 120.0) or 120.0),
        llm_seed=int(getattr(args, "llm_seed", 0) or 0),
        llm_consistency_weight=float(getattr(args, "llm_consistency_weight", 1.0) or 1.0),
        llm_model_weight=float(getattr(args, "llm_model_weight", 1.0) or 1.0),
        llm_augmentation_likelihood_weight=float(
            getattr(args, "llm_augmentation_likelihood_weight", 1.0) or 1.0
        ),
        llm_enable_neural_backend=bool(getattr(args, "llm_enable_neural_backend", False)),
        llm_model_path=getattr(args, "llm_model_path", None),
        llm_lora_path=getattr(args, "llm_lora_path", None),
        llm_max_runtime_sec=float(getattr(args, "llm_max_runtime_sec", 0.0) or 0.0),
        llm_task_runtime_sec=float(getattr(args, "llm_task_runtime_sec", 0.0) or 0.0),
        llm_decode_runtime_sec=float(getattr(args, "llm_decode_runtime_sec", 0.0) or 0.0),
        llm_adapt_steps=int(getattr(args, "llm_adapt_steps", 0) or 0),
        llm_adapt_batch_size=int(getattr(args, "llm_adapt_batch_size", 1) or 1),
        llm_adapt_gradient_accumulation_steps=int(
            getattr(args, "llm_adapt_gradient_accumulation_steps", 1) or 1
        ),
        llm_adapt_disabled=bool(getattr(args, "llm_adapt_disabled", False)),
        llm_per_task_adaptation=bool(getattr(args, "llm_per_task_adaptation", False)),
        llm_runtime_attention_mode=str(getattr(args, "llm_runtime_attention_mode", "auto") or "auto"),
        llm_runtime_disable_compile=bool(getattr(args, "llm_runtime_disable_compile", False)),
        llm_runtime_allocator_expandable_segments=bool(
            getattr(args, "llm_runtime_allocator_expandable_segments", True)
        ),
        llm_runtime_allocator_max_split_size_mb=int(
            getattr(args, "llm_runtime_allocator_max_split_size_mb", 0) or 0
        ),
        llm_prefer_cnn_attempt1=bool(getattr(args, "llm_prefer_cnn_attempt1", False)),
        llm_candidate_ranker=str(getattr(args, "llm_candidate_ranker", "default") or "default"),
        llm_infer_artifact_dir=getattr(args, "llm_infer_artifact_dir", None),
        llm_infer_artifact_run_name=str(getattr(args, "llm_infer_artifact_run_name", "") or ""),
    )
    _log_result(result)


def score_submission_cmd(args: argparse.Namespace) -> None:
    try:
        out = pipeline_run_score_submission(
            data_root=resolve_data_root_from_args(args),
            submission_path=str(getattr(args, "submission", "")),
            split=str(getattr(args, "split", "evaluation")),
        )
        logger.info("✅ score_submission score=%s paths=%s", out.get("score"), {k: out[k] for k in ("challenges_path", "solutions_path", "submission_path")})
    except Exception as e:
        logger.error("❌ score_submission failed: %s", e)
        raise


def benchmark_rankers_cmd(args: argparse.Namespace) -> None:
    try:
        out = pipeline_run_benchmark_rankers_from_artifacts(
            data_root=resolve_data_root_from_args(args),
            decoded_dir=str(getattr(args, "decoded_dir", "")),
            split=str(getattr(args, "split", "evaluation")),
            n_guesses=int(getattr(args, "n_guesses", 2) or 2),
            max_targets=int(getattr(args, "max_targets", 0) or 0),
        )
        logger.info("✅ benchmark_rankers summary=%s", out)
    except Exception as e:
        logger.error("❌ benchmark_rankers failed: %s", e)
        raise


def train_and_submit(args: argparse.Namespace) -> None:
    validate_arc_optional_args(args)
    run = init_run_context(
        stage="train_and_submit",
        data_root=resolve_data_root_from_args(args),
        seed=int(getattr(args, "seed", 42)),
        run_id=getattr(args, "run_id", None),
        run_dir=getattr(args, "run_dir", None),
    )
    result = run_train_and_submit_pipeline_result(
        data_root=resolve_data_root_from_args(args),
        train_mode=str(getattr(args, "train_mode", "end_to_end")),
        models=parse_models_csv(getattr(args, "models", None)),
        strategy=str(getattr(args, "strategy", "single")),
        output_json=getattr(args, "output_csv", None),
        max_targets=int(getattr(args, "max_targets", 0) or 0),
        run_ctx=run,
        llm_execution_mode=str(getattr(args, "llm_execution_mode", "surrogate") or "surrogate"),
        llm_num_augmentations=int(getattr(args, "llm_num_augmentations", 8) or 8),
        llm_beam_width=int(getattr(args, "llm_beam_width", 12) or 12),
        llm_max_candidates=int(getattr(args, "llm_max_candidates", 6) or 6),
        llm_max_neg_log_score=float(getattr(args, "llm_max_neg_log_score", 120.0) or 120.0),
        llm_seed=int(getattr(args, "llm_seed", 0) or 0),
        llm_consistency_weight=float(getattr(args, "llm_consistency_weight", 1.0) or 1.0),
        llm_model_weight=float(getattr(args, "llm_model_weight", 1.0) or 1.0),
        llm_augmentation_likelihood_weight=float(
            getattr(args, "llm_augmentation_likelihood_weight", 1.0) or 1.0
        ),
        llm_enable_neural_backend=bool(getattr(args, "llm_enable_neural_backend", False)),
        llm_model_path=getattr(args, "llm_model_path", None),
        llm_lora_path=getattr(args, "llm_lora_path", None),
        llm_max_runtime_sec=float(getattr(args, "llm_max_runtime_sec", 0.0) or 0.0),
        llm_task_runtime_sec=float(getattr(args, "llm_task_runtime_sec", 0.0) or 0.0),
        llm_decode_runtime_sec=float(getattr(args, "llm_decode_runtime_sec", 0.0) or 0.0),
        llm_adapt_steps=int(getattr(args, "llm_adapt_steps", 0) or 0),
        llm_adapt_batch_size=int(getattr(args, "llm_adapt_batch_size", 1) or 1),
        llm_adapt_gradient_accumulation_steps=int(
            getattr(args, "llm_adapt_gradient_accumulation_steps", 1) or 1
        ),
        llm_adapt_disabled=bool(getattr(args, "llm_adapt_disabled", False)),
        llm_per_task_adaptation=bool(getattr(args, "llm_per_task_adaptation", False)),
        llm_runtime_attention_mode=str(getattr(args, "llm_runtime_attention_mode", "auto") or "auto"),
        llm_runtime_disable_compile=bool(getattr(args, "llm_runtime_disable_compile", False)),
        llm_runtime_allocator_expandable_segments=bool(
            getattr(args, "llm_runtime_allocator_expandable_segments", True)
        ),
        llm_runtime_allocator_max_split_size_mb=int(
            getattr(args, "llm_runtime_allocator_max_split_size_mb", 0) or 0
        ),
        llm_prefer_cnn_attempt1=bool(getattr(args, "llm_prefer_cnn_attempt1", False)),
        llm_candidate_ranker=str(getattr(args, "llm_candidate_ranker", "default") or "default"),
        llm_infer_artifact_dir=getattr(args, "llm_infer_artifact_dir", None),
        llm_infer_artifact_run_name=str(getattr(args, "llm_infer_artifact_run_name", "") or ""),
    )
    _log_result(result)


def tune_and_submit(args: argparse.Namespace) -> None:
    validate_arc_optional_args(args)
    run = init_run_context(
        stage="tune_and_submit",
        data_root=resolve_data_root_from_args(args),
        seed=int(getattr(args, "seed", 42)),
        run_id=getattr(args, "run_id", None),
        run_dir=getattr(args, "run_dir", None),
    )
    result = run_tune_and_submit_pipeline_result(
        data_root=resolve_data_root_from_args(args),
        model_name=str(getattr(args, "model", "baseline_approx")),
        search_type=str(getattr(args, "search_type", "quick")),
        strategy=str(getattr(args, "strategy", "single")),
        output_json=getattr(args, "output_csv", None),
        max_targets=int(getattr(args, "max_targets", 0) or 0),
        run_ctx=run,
        llm_execution_mode=str(getattr(args, "llm_execution_mode", "surrogate") or "surrogate"),
        llm_num_augmentations=int(getattr(args, "llm_num_augmentations", 8) or 8),
        llm_beam_width=int(getattr(args, "llm_beam_width", 12) or 12),
        llm_max_candidates=int(getattr(args, "llm_max_candidates", 6) or 6),
        llm_max_neg_log_score=float(getattr(args, "llm_max_neg_log_score", 120.0) or 120.0),
        llm_seed=int(getattr(args, "llm_seed", 0) or 0),
        llm_consistency_weight=float(getattr(args, "llm_consistency_weight", 1.0) or 1.0),
        llm_model_weight=float(getattr(args, "llm_model_weight", 1.0) or 1.0),
        llm_augmentation_likelihood_weight=float(
            getattr(args, "llm_augmentation_likelihood_weight", 1.0) or 1.0
        ),
        llm_enable_neural_backend=bool(getattr(args, "llm_enable_neural_backend", False)),
        llm_model_path=getattr(args, "llm_model_path", None),
        llm_lora_path=getattr(args, "llm_lora_path", None),
        llm_max_runtime_sec=float(getattr(args, "llm_max_runtime_sec", 0.0) or 0.0),
        llm_task_runtime_sec=float(getattr(args, "llm_task_runtime_sec", 0.0) or 0.0),
        llm_decode_runtime_sec=float(getattr(args, "llm_decode_runtime_sec", 0.0) or 0.0),
        llm_adapt_steps=int(getattr(args, "llm_adapt_steps", 0) or 0),
        llm_adapt_batch_size=int(getattr(args, "llm_adapt_batch_size", 1) or 1),
        llm_adapt_gradient_accumulation_steps=int(
            getattr(args, "llm_adapt_gradient_accumulation_steps", 1) or 1
        ),
        llm_adapt_disabled=bool(getattr(args, "llm_adapt_disabled", False)),
        llm_per_task_adaptation=bool(getattr(args, "llm_per_task_adaptation", False)),
        llm_runtime_attention_mode=str(getattr(args, "llm_runtime_attention_mode", "auto") or "auto"),
        llm_runtime_disable_compile=bool(getattr(args, "llm_runtime_disable_compile", False)),
        llm_runtime_allocator_expandable_segments=bool(
            getattr(args, "llm_runtime_allocator_expandable_segments", True)
        ),
        llm_runtime_allocator_max_split_size_mb=int(
            getattr(args, "llm_runtime_allocator_max_split_size_mb", 0) or 0
        ),
        llm_prefer_cnn_attempt1=bool(getattr(args, "llm_prefer_cnn_attempt1", False)),
        llm_candidate_ranker=str(getattr(args, "llm_candidate_ranker", "default") or "default"),
        llm_infer_artifact_dir=getattr(args, "llm_infer_artifact_dir", None),
        llm_infer_artifact_run_name=str(getattr(args, "llm_infer_artifact_run_name", "") or ""),
    )
    _log_result(result)


def _log_result(result: PipelineResult) -> None:
    if result.success:
        logger.info("✅ %s succeeded", result.stage)
        if result.artifacts:
            logger.info("  artifacts=%s", dict(result.artifacts))
        if result.metadata:
            logger.info("  metadata=%s", dict(result.metadata))
        return
    logger.error("❌ %s failed", result.stage)
    if result.error:
        logger.error("  error=%s", result.error)
    if result.metadata:
        logger.error("  metadata=%s", dict(result.metadata))


def get_handlers() -> dict[str, Callable]:
    return {
        "validate_data": validate_data,
        "train": train,
        "tune": tune,
        "submit": submit,
        "score_submission": score_submission_cmd,
        "benchmark_rankers": benchmark_rankers_cmd,
        "train_and_submit": train_and_submit,
        "tune_and_submit": tune_and_submit,
    }
