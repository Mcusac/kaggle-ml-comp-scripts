"""argparse handlers that delegate to the ``level_6`` pipeline-result functions."""

import argparse

from layers.layer_1_competition.level_0_infra.level_0 import (
    llm_tta_kwargs_from_args,
    log_result,
)
from layers.layer_1_competition.level_0_infra.level_1 import (
    parse_models_csv,
    resolve_data_root_from_args,
)

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2 import (
    init_run_context,
    run_validate_data_pipeline,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_6 import (
    run_submission_pipeline_result,
    run_train_pipeline_result,
    run_tune_pipeline_result,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_7 import (
    run_train_and_submit_pipeline_result,
    run_tune_and_submit_pipeline_result,
)


def validate_data(args: argparse.Namespace) -> None:
    result = run_validate_data_pipeline(
        data_root=resolve_data_root_from_args(args),
        max_targets=int(getattr(args, "max_targets", 0) or 0),
        run_ctx=None,
    )
    log_result(result)


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
    log_result(result)


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
    log_result(result)


def submit(args: argparse.Namespace) -> None:
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
        **llm_tta_kwargs_from_args(args),
    )
    log_result(result)


def train_and_submit(args: argparse.Namespace) -> None:
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
        **llm_tta_kwargs_from_args(args),
    )
    log_result(result)


def tune_and_submit(args: argparse.Namespace) -> None:
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
        **llm_tta_kwargs_from_args(args),
    )
    log_result(result)
