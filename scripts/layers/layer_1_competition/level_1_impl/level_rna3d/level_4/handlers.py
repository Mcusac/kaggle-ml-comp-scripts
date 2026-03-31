"""RNA3D handlers."""

import argparse

from typing import Any, Callable, Dict, List, Optional

from layers.layer_1_competition.level_1_impl.level_rna3d.level_0.validate_data import (
    validate_rna3d_inputs,
)
from layers.layer_1_competition.level_1_impl.level_rna3d.level_2 import (
    submit_pipeline,
    run_train_and_submit_pipeline_result,
    tune_pipeline,
)
from layers.layer_1_competition.level_1_impl.level_rna3d.level_3 import train_pipeline
from layers.layer_1_competition.level_0_infra.level_1.contest import (
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

# Framework `setup_framework_subparsers` omits these names when contest is rna3d so this
# module can register contest-specific train/submit parsers without argparse conflicts.
FRAMEWORK_SUBPARSER_NAMES_TO_SKIP = frozenset({"train", "submit"})


def extend_subparsers(subparsers: Any) -> None:
    """Register RNA3D subcommands (train/submit registered here; framework skips those names)."""
    tr = subparsers.add_parser(
        "train",
        help="Train RNA3D models (contest-specific; replaces framework train when contest is rna3d)",
    )
    add_common_contest_args(tr)
    add_train_mode_arg(
        tr,
        default="end_to_end",
        help_text="Training pipeline label (e.g. end_to_end, multi_part)",
    )
    add_models_arg(
        tr,
        default="baseline_approx",
        help_text="Comma-separated model names (e.g. baseline_approx)",
    )

    tu = subparsers.add_parser("tune", help="Tune RNA3D model hyperparameters")
    add_common_contest_args(tu)
    tu.set_defaults(model="baseline_approx")
    tu.add_argument(
        "--search-type",
        type=str,
        choices=["quick", "thorough"],
        default="quick",
        help="Hyperparameter search breadth",
    )
    tu.add_argument(
        "--max-targets",
        type=int,
        default=0,
        help="If >0, only use the first N validation targets",
    )

    su = subparsers.add_parser(
        "submit",
        help="Generate RNA3D submission CSV (contest-specific; replaces framework submit)",
    )
    add_common_contest_args(su)
    add_strategy_arg(
        su,
        choices=("single", "ensemble", "stacking", "stacking_ensemble"),
        default="single",
        help_text="Submission strategy",
    )
    add_models_arg(
        su,
        default="baseline_approx",
        help_text="Comma-separated model names",
    )
    add_output_csv_arg(su, help_text="Optional output CSV path")
    add_max_targets_arg(
        su,
        default=0,
        help_text="If >0, only predict for the first N test targets",
    )
    add_ensemble_weights_arg(
        su,
        help_text="Comma-separated weights for ensemble/stacking",
    )
    add_validation_stacking_toggle(
        su,
        default=True,
        help_text="Do not fit stacking weights from validation when applicable",
    )

    ts = subparsers.add_parser(
        "train_and_submit",
        help="Validate -> train -> submit (PipelineResult composite)",
    )
    add_common_contest_args(ts)
    add_train_mode_arg(ts, default="end_to_end", help_text=None)
    add_models_arg(ts, default="baseline_approx", help_text=None)
    add_strategy_arg(
        ts,
        choices=("single", "ensemble", "stacking", "stacking_ensemble"),
        default="single",
        help_text=None,
    )
    add_output_csv_arg(ts, help_text=None)
    add_max_targets_arg(ts, default=0, help_text=None)
    add_ensemble_weights_arg(ts, help_text=None)
    add_validation_stacking_toggle(ts, default=True, help_text=None)

    vd = subparsers.add_parser(
        "validate_data",
        help="Validate RNA3D CSV inputs under --data-root",
    )
    add_common_contest_args(vd)
    add_max_targets_arg(
        vd,
        default=0,
        help_text="If >0, only validate the first N test targets in depth",
    )


def validate_data(args: argparse.Namespace) -> None:
    root = resolve_data_root_from_args(args)
    max_targets = int(getattr(args, "max_targets", 0) or 0)
    validate_rna3d_inputs(root, max_targets=max_targets)


def train(args: argparse.Namespace) -> None:
    train_pipeline(
        data_root=resolve_data_root_from_args(args),
        train_mode=getattr(args, "train_mode", "end_to_end"),
        models=parse_models_csv(getattr(args, "models", None)),
    )


def tune(args: argparse.Namespace) -> None:
    tune_pipeline(
        data_root=resolve_data_root_from_args(args),
        model_name=args.model,
        search_type=args.search_type,
        max_targets=int(getattr(args, "max_targets", 0) or 0),
    )


def submit(args: argparse.Namespace) -> None:
    submit_pipeline(
        data_root=resolve_data_root_from_args(args),
        strategy=args.strategy,
        models=parse_models_csv(getattr(args, "models", None)),
        output_csv=getattr(args, "output_csv", None),
        max_targets=int(getattr(args, "max_targets", 0) or 0),
        ensemble_weights=parse_optional_float_list(getattr(args, "ensemble_weights", None)),
        use_validation_for_stacking=bool(getattr(args, "use_validation_for_stacking", True)),
    )


def train_and_submit(args: argparse.Namespace) -> None:
    run_train_and_submit_pipeline_result(
        data_root=resolve_data_root_from_args(args),
        train_mode=getattr(args, "train_mode", "end_to_end"),
        models=parse_models_csv(getattr(args, "models", None)),
        strategy=str(getattr(args, "strategy", "single")),
        output_csv=getattr(args, "output_csv", None),
        max_targets=int(getattr(args, "max_targets", 0) or 0),
        ensemble_weights=parse_optional_float_list(getattr(args, "ensemble_weights", None)),
        use_validation_for_stacking=bool(getattr(args, "use_validation_for_stacking", True)),
        validate_first=True,
    )


def get_handlers() -> Dict[str, Callable]:
    return {
        "validate_data": validate_data,
        "train": train,
        "tune": tune,
        "submit": submit,
        "train_and_submit": train_and_submit,
    }
