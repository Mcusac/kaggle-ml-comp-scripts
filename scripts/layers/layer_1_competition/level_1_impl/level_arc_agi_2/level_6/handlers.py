"""ARC contest handlers."""

import argparse

from typing import Any, Callable

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_0_infra.level_1 import (
    add_common_contest_args,
    add_ensemble_weights_arg,
    add_max_targets_arg,
    add_models_arg,
    add_output_csv_arg,
    add_strategy_arg,
    add_train_mode_arg,
    add_validation_stacking_toggle,
    parse_models_csv,
    parse_optional_float_list,
    resolve_data_root_from_args,
)

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import PipelineResult, init_run_context
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_4 import (
    pipeline_run_benchmark_rankers_from_artifacts,
    pipeline_run_score_submission,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_5 import (
    run_submission_pipeline_result,
    run_train_and_submit_pipeline_result,
    run_train_pipeline_result,
    run_tune_and_submit_pipeline_result,
    run_tune_pipeline_result,
    run_validate_data_pipeline,
)

logger = get_logger(__name__)

FRAMEWORK_SUBPARSER_NAMES_TO_SKIP = frozenset({"train", "submit"})


def _add_llm_tta_args(parser: Any) -> None:
    parser.add_argument(
        "--llm-execution-mode",
        choices=("surrogate", "lm_backend"),
        default="surrogate",
        help="llm_tta_dfs execution mode.",
    )
    parser.add_argument("--llm-num-augmentations", type=int, default=8, help="Number of ARC TTA augmentations.")
    parser.add_argument("--llm-beam-width", type=int, default=12, help="Beam width for constrained decoder.")
    parser.add_argument("--llm-max-candidates", type=int, default=6, help="Max candidate grids per augmentation.")
    parser.add_argument("--llm-max-neg-log-score", type=float, default=120.0, help="Prune beams above this -log score.")
    parser.add_argument("--llm-seed", type=int, default=0, help="Deterministic seed for augmentation sampling.")
    parser.add_argument(
        "--llm-consistency-weight",
        type=float,
        default=1.0,
        help="Weight for augmentation agreement in candidate ranking.",
    )
    parser.add_argument(
        "--llm-model-weight",
        type=float,
        default=1.0,
        help="Weight for model score term in candidate ranking.",
    )
    parser.add_argument(
        "--llm-enable-neural-backend",
        action="store_true",
        help="Enable neural backend path in llm_tta_dfs when available.",
    )
    parser.add_argument("--llm-model-path", type=str, default=None, help="Optional base LLM model path.")
    parser.add_argument("--llm-lora-path", type=str, default=None, help="Optional LoRA adapter path.")
    parser.add_argument("--llm-max-runtime-sec", type=float, default=0.0, help="Optional max runtime budget.")
    parser.add_argument("--llm-task-runtime-sec", type=float, default=0.0, help="Optional per-task budget.")
    parser.add_argument("--llm-decode-runtime-sec", type=float, default=0.0, help="Optional per-decode budget.")
    parser.add_argument("--llm-adapt-steps", type=int, default=0, help="Optional adaptation steps.")
    parser.add_argument("--llm-adapt-batch-size", type=int, default=1, help="Adaptation batch size.")
    parser.add_argument(
        "--llm-adapt-gradient-accumulation-steps",
        type=int,
        default=1,
        help="Adaptation gradient accumulation steps.",
    )
    parser.add_argument("--llm-adapt-disabled", action="store_true", help="Disable task adaptation.")
    parser.add_argument(
        "--llm-augmentation-likelihood-weight",
        type=float,
        default=1.0,
        help="Weight for augmentation-likelihood score term.",
    )
    parser.add_argument(
        "--llm-runtime-attention-mode",
        choices=("auto", "eager", "sdpa"),
        default="auto",
        help="Runtime attention mode hint for LM backend.",
    )
    parser.add_argument(
        "--llm-runtime-disable-compile",
        action="store_true",
        help="Disable compile-related paths in runtime profile.",
    )
    parser.add_argument(
        "--llm-runtime-allocator-expandable-segments",
        action="store_true",
        default=True,
        help="Enable expandable segments allocator profile.",
    )
    parser.add_argument(
        "--llm-runtime-allocator-max-split-size-mb",
        type=int,
        default=0,
        help="Optional allocator max split size.",
    )
    parser.add_argument(
        "--llm-prefer-cnn-attempt1",
        action="store_true",
        help="When CNN checkpoint is available, prefer CNN for attempt_1 over llm_tta path.",
    )
    parser.add_argument(
        "--llm-candidate-ranker",
        choices=("default", "kgmon", "probmul"),
        default="default",
        help="Candidate merge ranker for llm_tta_dfs (default=weighted package ranker).",
    )


def _validate_arc_optional_args(args: argparse.Namespace) -> None:
    weights = getattr(args, "ensemble_weights", None)
    if weights and str(weights).strip():
        # Parse for input validation, then fail explicitly to avoid silent no-op.
        parse_optional_float_list(weights)
        raise ValueError("ARC submit path does not use --ensemble-weights. Remove this flag.")
    if getattr(args, "use_validation_for_stacking", True) is False:
        raise ValueError("ARC does not support stacking strategies; --no-validation-stacking is not applicable.")


def extend_subparsers(subparsers: Any) -> None:
    train = subparsers.add_parser(
        "train",
        help="Train ARC models: neural (e.g. grid_cnn_v0) via PyTorch or baseline heuristics from training JSON",
    )
    add_common_contest_args(train)
    add_train_mode_arg(
        train,
        default="end_to_end",
        help_text="quick|end_to_end: heuristic scoring breadth",
    )
    add_models_arg(
        train,
        default="baseline_approx",
        help_text="Comma-separated: baseline_approx | grid_cnn_v0 | …",
    )
    add_max_targets_arg(
        train,
        default=0,
        help_text="Cap train pairs per task for heuristic scoring (0=all)",
    )
    train.add_argument("--run-id", type=str, help="Optional run id for run folder tracking")
    train.add_argument("--run-dir", type=str, help="Optional explicit run folder path")

    tune = subparsers.add_parser("tune", help="Tune ARC heuristic on evaluation split (needs eval solutions)")
    add_common_contest_args(tune)
    tune.add_argument("--search-type", choices=["quick", "thorough"], default="quick")
    tune.set_defaults(model="baseline_approx")
    tune.add_argument("--max-targets", type=int, default=0)
    tune.add_argument("--run-id", type=str, help="Optional run id for run folder tracking")
    tune.add_argument("--run-dir", type=str, help="Optional explicit run folder path")

    submit = subparsers.add_parser("submit", help="Generate submission.json (heuristic and/or neural from train metadata)")
    add_common_contest_args(submit)
    add_strategy_arg(
        submit,
        choices=("single", "ensemble", "llm_tta_dfs", "stacking", "stacking_ensemble"),
        default="single",
        help_text="single|ensemble|llm_tta_dfs: ARC submit strategies; stacking* not implemented (fails)",
    )
    add_models_arg(
        submit,
        default="baseline_approx",
        help_text="Primary model name (must match train_metadata per_model); use grid_cnn_v0 after training that model",
    )
    submit.add_argument("--train-mode", type=str, default="end_to_end", help="Used for ensemble heuristic ranking")
    add_output_csv_arg(submit, help_text="Optional output JSON path")
    add_max_targets_arg(submit, default=0, help_text=None)
    add_ensemble_weights_arg(submit, help_text=None)
    add_validation_stacking_toggle(submit, default=True, help_text=None)
    submit.add_argument("--run-id", type=str, help="Optional run id for run folder tracking")
    submit.add_argument("--run-dir", type=str, help="Optional explicit run folder path")
    submit.add_argument(
        "--tuned-config",
        type=str,
        default=None,
        help="Optional path to best_config.json from tune",
    )
    submit.add_argument(
        "--neural-checkpoint",
        type=str,
        default=None,
        help="Override neural weights path (default: from train_metadata per_model.artifacts)",
    )
    submit.add_argument(
        "--neural-train-config",
        type=str,
        default=None,
        help="Override train_config.json path for neural inference",
    )
    _add_llm_tta_args(submit)

    validate = subparsers.add_parser("validate_data", help="Validate ARC JSON inputs")
    add_common_contest_args(validate)
    validate.add_argument("--max-targets", type=int, default=0)

    score_sub = subparsers.add_parser(
        "score_submission",
        help="Score a submission.json against evaluation challenges+solutions (local LB-style).",
    )
    add_common_contest_args(score_sub)
    score_sub.add_argument(
        "--submission",
        type=str,
        required=True,
        help="Path to submission.json",
    )
    score_sub.add_argument(
        "--split",
        type=str,
        default="evaluation",
        choices=("evaluation",),
        help="Only evaluation split is supported (public solutions).",
    )

    bench = subparsers.add_parser(
        "benchmark_rankers",
        help="Benchmark reference rankers on bz2 decode shards vs evaluation labels.",
    )
    add_common_contest_args(bench)
    bench.add_argument("--decoded-dir", type=str, required=True, help="Directory of .bz2 pickle shards.")
    bench.add_argument(
        "--split",
        type=str,
        default="evaluation",
        choices=("evaluation",),
        help="Split for labels (evaluation only).",
    )
    bench.add_argument("--n-guesses", type=int, default=2)
    bench.add_argument("--max-targets", type=int, default=0)

    train_submit = subparsers.add_parser("train_and_submit", help="Train then submit (validate once)")
    add_common_contest_args(train_submit)
    add_train_mode_arg(train_submit, default="end_to_end", help_text=None)
    add_models_arg(train_submit, default="grid_cnn_v0", help_text=None)
    add_strategy_arg(
        train_submit,
        choices=("single", "ensemble", "llm_tta_dfs", "stacking", "stacking_ensemble"),
        default="single",
        help_text=None,
    )
    add_output_csv_arg(train_submit, help_text="Optional output JSON path")
    add_max_targets_arg(train_submit, default=0, help_text=None)
    add_ensemble_weights_arg(train_submit, help_text=None)
    add_validation_stacking_toggle(train_submit, default=True, help_text=None)
    train_submit.add_argument("--run-id", type=str, help="Optional run id for run folder tracking")
    train_submit.add_argument("--run-dir", type=str, help="Optional explicit run folder path")
    _add_llm_tta_args(train_submit)

    tune_submit = subparsers.add_parser("tune_and_submit", help="Tune then generate submission (validate once)")
    add_common_contest_args(tune_submit)
    tune_submit.add_argument("--search-type", choices=["quick", "thorough"], default="quick")
    tune_submit.set_defaults(model="baseline_approx")
    add_strategy_arg(
        tune_submit,
        choices=("single", "ensemble", "llm_tta_dfs", "stacking", "stacking_ensemble"),
        default="single",
        help_text=None,
    )
    add_models_arg(tune_submit, default="baseline_approx")
    add_output_csv_arg(tune_submit, help_text="Optional output JSON path")
    add_max_targets_arg(tune_submit, default=0, help_text=None)
    add_ensemble_weights_arg(tune_submit, help_text=None)
    add_validation_stacking_toggle(tune_submit, default=True, help_text=None)
    tune_submit.add_argument("--run-id", type=str, help="Optional run id for run folder tracking")
    tune_submit.add_argument("--run-dir", type=str, help="Optional explicit run folder path")
    _add_llm_tta_args(tune_submit)


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
    _validate_arc_optional_args(args)
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
    _validate_arc_optional_args(args)
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
    )
    _log_result(result)


def tune_and_submit(args: argparse.Namespace) -> None:
    _validate_arc_optional_args(args)
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
