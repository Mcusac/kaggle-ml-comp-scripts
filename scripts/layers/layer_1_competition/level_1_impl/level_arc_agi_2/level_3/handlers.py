"""ARC contest handlers."""

import argparse

from typing import Any, Callable

from layers.layer_1_competition.level_0_infra.level_1.contest import (
    add_common_contest_args,
    resolve_data_root_from_args,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.validate_data import (
    validate_arc_inputs,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    init_run_context,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2 import (
    run_submission_pipeline,
    run_train_pipeline,
    run_tune_pipeline,
)

FRAMEWORK_SUBPARSER_NAMES_TO_SKIP = frozenset({"train", "submit"})


def _parse_models_csv(raw: str | None) -> list[str]:
    if not raw or not str(raw).strip():
        return ["baseline_approx"]
    return [piece.strip() for piece in str(raw).split(",") if piece.strip()]


def _parse_optional_float_list(raw: str | None) -> list[float] | None:
    if not raw or not str(raw).strip():
        return None
    return [float(x.strip()) for x in str(raw).split(",") if x.strip()]


def extend_subparsers(subparsers: Any) -> None:
    train = subparsers.add_parser("train", help="Train ARC starter pipeline")
    add_common_contest_args(train)
    train.add_argument("--train-mode", type=str, default="end_to_end")
    train.add_argument("--models", type=str, default="baseline_approx")
    train.add_argument("--run-id", type=str, help="Optional run id for run folder tracking")
    train.add_argument("--run-dir", type=str, help="Optional explicit run folder path")

    tune = subparsers.add_parser("tune", help="Tune ARC starter pipeline")
    add_common_contest_args(tune)
    tune.add_argument("--search-type", choices=["quick", "thorough"], default="quick")
    tune.set_defaults(model="baseline_approx")
    tune.add_argument("--max-targets", type=int, default=0)
    tune.add_argument("--run-id", type=str, help="Optional run id for run folder tracking")
    tune.add_argument("--run-dir", type=str, help="Optional explicit run folder path")

    submit = subparsers.add_parser("submit", help="Generate ARC submission.json")
    add_common_contest_args(submit)
    submit.add_argument(
        "--strategy",
        choices=["single", "ensemble", "stacking", "stacking_ensemble"],
        default="single",
    )
    submit.add_argument("--models", type=str, default="baseline_approx")
    submit.add_argument("--output-csv", type=str, help="Optional output JSON path")
    submit.add_argument("--max-targets", type=int, default=0)
    submit.add_argument("--ensemble-weights", type=str)
    submit.set_defaults(use_validation_for_stacking=True)
    submit.add_argument(
        "--no-validation-stacking",
        dest="use_validation_for_stacking",
        action="store_false",
    )
    submit.add_argument("--run-id", type=str, help="Optional run id for run folder tracking")
    submit.add_argument("--run-dir", type=str, help="Optional explicit run folder path")

    validate = subparsers.add_parser("validate_data", help="Validate ARC JSON inputs")
    add_common_contest_args(validate)
    validate.add_argument("--max-targets", type=int, default=0)


def validate_data(args: argparse.Namespace) -> None:
    validate_arc_inputs(
        data_root=resolve_data_root_from_args(args),
        max_targets=int(getattr(args, "max_targets", 0) or 0),
    )


def train(args: argparse.Namespace) -> None:
    run = init_run_context(
        stage="train",
        data_root=resolve_data_root_from_args(args),
        seed=int(getattr(args, "seed", 42)),
        run_id=getattr(args, "run_id", None),
        run_dir=getattr(args, "run_dir", None),
    )
    run_train_pipeline(
        data_root=resolve_data_root_from_args(args),
        train_mode=str(getattr(args, "train_mode", "end_to_end")),
        models=_parse_models_csv(getattr(args, "models", None)),
        run_ctx=run,
    )


def tune(args: argparse.Namespace) -> None:
    run = init_run_context(
        stage="tune",
        data_root=resolve_data_root_from_args(args),
        seed=int(getattr(args, "seed", 42)),
        run_id=getattr(args, "run_id", None),
        run_dir=getattr(args, "run_dir", None),
    )
    run_tune_pipeline(
        data_root=resolve_data_root_from_args(args),
        model_name=str(getattr(args, "model", "baseline_approx")),
        search_type=str(getattr(args, "search_type", "quick")),
        max_targets=int(getattr(args, "max_targets", 0) or 0),
        run_ctx=run,
    )


def submit(args: argparse.Namespace) -> None:
    _parse_optional_float_list(getattr(args, "ensemble_weights", None))
    run = init_run_context(
        stage="submit",
        data_root=resolve_data_root_from_args(args),
        seed=int(getattr(args, "seed", 42)),
        run_id=getattr(args, "run_id", None),
        run_dir=getattr(args, "run_dir", None),
    )
    run_submission_pipeline(
        data_root=resolve_data_root_from_args(args),
        strategy=str(getattr(args, "strategy", "single")),
        output_json=getattr(args, "output_csv", None),
        max_targets=int(getattr(args, "max_targets", 0) or 0),
        run_ctx=run,
    )


def get_handlers() -> dict[str, Callable]:
    return {
        "validate_data": validate_data,
        "train": train,
        "tune": tune,
        "submit": submit,
    }

