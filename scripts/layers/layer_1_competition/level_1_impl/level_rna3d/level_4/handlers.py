"""RNA3D handlers."""

import argparse

from typing import Any, Callable, Dict, List, Optional

from layers.layer_1_competition.level_1_impl.level_rna3d.level_0.validate_data import (
    validate_rna3d_inputs,
)
from layers.layer_1_competition.level_1_impl.level_rna3d.level_2 import (
    submit_pipeline,
    tune_pipeline,
)
from layers.layer_1_competition.level_1_impl.level_rna3d.level_3 import train_pipeline
from layers.layer_1_competition.level_0_infra.level_1.contest import (
    add_common_contest_args,
    resolve_data_root_from_args,
)

# Framework `setup_framework_subparsers` omits these names when contest is rna3d so this
# module can register contest-specific train/submit parsers without argparse conflicts.
FRAMEWORK_SUBPARSER_NAMES_TO_SKIP = frozenset({"train", "submit"})


def _parse_models_csv(raw: Optional[str]) -> List[str]:
    if not raw or not str(raw).strip():
        return ["baseline_approx"]
    return [p.strip() for p in str(raw).split(",") if p.strip()]


def _parse_optional_float_list(raw: Optional[str]) -> Optional[List[float]]:
    if not raw or not str(raw).strip():
        return None
    return [float(x.strip()) for x in str(raw).split(",") if x.strip()]


def extend_subparsers(subparsers: Any) -> None:
    """Register RNA3D subcommands (train/submit registered here; framework skips those names)."""
    tr = subparsers.add_parser(
        "train",
        help="Train RNA3D models (contest-specific; replaces framework train when contest is rna3d)",
    )
    add_common_contest_args(tr)
    tr.add_argument(
        "--train-mode",
        type=str,
        default="end_to_end",
        help="Training pipeline label (e.g. end_to_end, multi_part)",
    )
    tr.add_argument(
        "--models",
        type=str,
        default="baseline_approx",
        help="Comma-separated model names (e.g. baseline_approx)",
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
    su.add_argument(
        "--strategy",
        choices=["single", "ensemble", "stacking", "stacking_ensemble"],
        default="single",
        help="Submission strategy",
    )
    su.add_argument(
        "--models",
        type=str,
        default="baseline_approx",
        help="Comma-separated model names",
    )
    su.add_argument("--output-csv", type=str, help="Optional output CSV path")
    su.add_argument(
        "--max-targets",
        type=int,
        default=0,
        help="If >0, only predict for the first N test targets",
    )
    su.add_argument(
        "--ensemble-weights",
        type=str,
        help="Comma-separated weights for ensemble/stacking",
    )
    su.set_defaults(use_validation_for_stacking=True)
    su.add_argument(
        "--no-validation-stacking",
        dest="use_validation_for_stacking",
        action="store_false",
        help="Do not fit stacking weights from validation when applicable",
    )

    vd = subparsers.add_parser(
        "validate_data",
        help="Validate RNA3D CSV inputs under --data-root",
    )
    add_common_contest_args(vd)
    vd.add_argument(
        "--max-targets",
        type=int,
        default=0,
        help="If >0, only validate the first N test targets in depth",
    )


def validate_data(args: argparse.Namespace) -> None:
    root = resolve_data_root_from_args(args)
    max_targets = int(getattr(args, "max_targets", 0) or 0)
    validate_rna3d_inputs(root, max_targets=max_targets)


def train(args: argparse.Namespace) -> None:
    train_pipeline(
        data_root=resolve_data_root_from_args(args),
        train_mode=getattr(args, "train_mode", "end_to_end"),
        models=_parse_models_csv(getattr(args, "models", None)),
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
        models=_parse_models_csv(getattr(args, "models", None)),
        output_csv=getattr(args, "output_csv", None),
        max_targets=int(getattr(args, "max_targets", 0) or 0),
        ensemble_weights=_parse_optional_float_list(getattr(args, "ensemble_weights", None)),
        use_validation_for_stacking=bool(getattr(args, "use_validation_for_stacking", True)),
    )


def get_handlers() -> Dict[str, Callable]:
    return {
        "validate_data": validate_data,
        "train": train,
        "tune": tune,
        "submit": submit,
    }
