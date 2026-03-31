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
    PipelineResult,
    init_run_context,
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


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _build_run_ctx(args: argparse.Namespace, stage: str) -> Any:
    """Build a run context from common CLI args and a stage label."""
    return init_run_context(
        stage=stage,
        data_root=resolve_data_root_from_args(args),
        seed=int(getattr(args, "seed", 42)),
        run_id=getattr(args, "run_id", None),
        run_dir=getattr(args, "run_dir", None),
    )


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


# ---------------------------------------------------------------------------
# CLI registration
# ---------------------------------------------------------------------------

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
        choices=("single", "ensemble", "stacking", "stacking_ensemble"),
        default="single",
        help_text="single|ensemble: heuristic or hybrid second attempt; stacking* not implemented (fails)",
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

    validate = subparsers.add_parser("validate_data", help="Validate ARC JSON inputs")
    add_common_contest_args(validate)
    validate.add_argument("--max-targets", type=int, default=0)

    train_submit = subparsers.add_parser("train_and_submit", help="Train then submit (validate once)")
    add_common_contest_args(train_submit)
    add_train_mode_arg(train_submit, default="end_to_end", help_text=None)
    add_models_arg(train_submit, default="grid_cnn_v0", help_text=None)
    add_strategy_arg(train_submit, choices=("single", "ensemble", "stacking", "stacking_ensemble"), default="single", help_text=None)
    add_output_csv_arg(train_submit, help_text="Optional output JSON path")
    add_max_targets_arg(train_submit, default=0, help_text=None)
    add_ensemble_weights_arg(train_submit, help_text=None)
    add_validation_stacking_toggle(train_submit, default=True, help_text=None)
    train_submit.add_argument("--run-id", type=str, help="Optional run id for run folder tracking")
    train_submit.add_argument("--run-dir", type=str, help="Optional explicit run folder path")

    tune_submit = subparsers.add_parser("tune_and_submit", help="Tune then generate submission (validate once)")
    add_common_contest_args(tune_submit)
    tune_submit.add_argument("--search-type", choices=["quick", "thorough"], default="quick")
    tune_submit.set_defaults(model="baseline_approx")
    add_strategy_arg(tune_submit, choices=("single", "ensemble", "stacking", "stacking_ensemble"), default="single", help_text=None)
    add_models_arg(tune_submit, default="baseline_approx")
    add_output_csv_arg(tune_submit, help_text="Optional output JSON path")
    add_max_targets_arg(tune_submit, default=0, help_text=None)
    add_ensemble_weights_arg(tune_submit, help_text=None)
    add_validation_stacking_toggle(tune_submit, default=True, help_text=None)
    tune_submit.add_argument("--run-id", type=str, help="Optional run id for run folder tracking")
    tune_submit.add_argument("--run-dir", type=str, help="Optional explicit run folder path")


# ---------------------------------------------------------------------------
# Handlers
# ---------------------------------------------------------------------------

def validate_data(args: argparse.Namespace) -> None:
    result = run_validate_data_pipeline(
        data_root=resolve_data_root_from_args(args),
        max_targets=int(getattr(args, "max_targets", 0) or 0),
        run_ctx=None,
    )
    _log_result(result)


def train(args: argparse.Namespace) -> None:
    result = run_train_pipeline_result(
        data_root=resolve_data_root_from_args(args),
        train_mode=str(getattr(args, "train_mode", "end_to_end")),
        models=parse_models_csv(getattr(args, "models", None)),
        max_targets=int(getattr(args, "max_targets", 0) or 0),
        run_ctx=_build_run_ctx(args, "train"),
    )
    _log_result(result)


def tune(args: argparse.Namespace) -> None:
    result = run_tune_pipeline_result(
        data_root=resolve_data_root_from_args(args),
        model_name=str(getattr(args, "model", "baseline_approx")),
        search_type=str(getattr(args, "search_type", "quick")),
        max_targets=int(getattr(args, "max_targets", 0) or 0),
        run_ctx=_build_run_ctx(args, "tune"),
    )
    _log_result(result)


def submit(args: argparse.Namespace) -> None:
    parse_optional_float_list(getattr(args, "ensemble_weights", None))
    result = run_submission_pipeline_result(
        data_root=resolve_data_root_from_args(args),
        strategy=str(getattr(args, "strategy", "single")),
        output_json=getattr(args, "output_csv", None),
        max_targets=int(getattr(args, "max_targets", 0) or 0),
        run_ctx=_build_run_ctx(args, "submit"),
        tuned_config_path=getattr(args, "tuned_config", None),
        models=parse_models_csv(getattr(args, "models", None)),
        neural_checkpoint_path=getattr(args, "neural_checkpoint", None),
        neural_train_config_path=getattr(args, "neural_train_config", None),
        train_mode=str(getattr(args, "train_mode", "end_to_end")),
    )
    _log_result(result)


def train_and_submit(args: argparse.Namespace) -> None:
    parse_optional_float_list(getattr(args, "ensemble_weights", None))
    result = run_train_and_submit_pipeline_result(
        data_root=resolve_data_root_from_args(args),
        train_mode=str(getattr(args, "train_mode", "end_to_end")),
        models=parse_models_csv(getattr(args, "models", None)),
        strategy=str(getattr(args, "strategy", "single")),
        output_json=getattr(args, "output_csv", None),
        max_targets=int(getattr(args, "max_targets", 0) or 0),
        run_ctx=_build_run_ctx(args, "train_and_submit"),
    )
    _log_result(result)


def tune_and_submit(args: argparse.Namespace) -> None:
    parse_optional_float_list(getattr(args, "ensemble_weights", None))
    result = run_tune_and_submit_pipeline_result(
        data_root=resolve_data_root_from_args(args),
        model_name=str(getattr(args, "model", "baseline_approx")),
        search_type=str(getattr(args, "search_type", "quick")),
        strategy=str(getattr(args, "strategy", "single")),
        output_json=getattr(args, "output_csv", None),
        max_targets=int(getattr(args, "max_targets", 0) or 0),
        run_ctx=_build_run_ctx(args, "tune_and_submit"),
    )
    _log_result(result)


# ---------------------------------------------------------------------------
# Handler registry
# ---------------------------------------------------------------------------

def get_handlers() -> dict[str, Callable[[argparse.Namespace], None]]:
    return {
        "validate_data": validate_data,
        "train": train,
        "tune": tune,
        "submit": submit,
        "train_and_submit": train_and_submit,
        "tune_and_submit": tune_and_submit,
    }