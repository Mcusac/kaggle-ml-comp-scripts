"""Shared helpers and constants for CSIRO CLI handlers."""

import argparse
from typing import Any

from layers.layer_1_competition.level_0_infra.level_1.contest import add_common_contest_args

CSIRO_COMMANDS = [
    "dataset_grid_search",
    "hyperparameter_grid_search",
    "regression_grid_search",
    "cleanup_grid_search",
    "submit_best",
    "train_and_export",
    "export_model",
    "csiro_ensemble",
    "regression_ensemble",
    "stacking",
    "stacking_ensemble",
    "hybrid_stacking",
    "multi_variant_regression_train",
    "submit",
]


def add_common_args(parser: argparse.ArgumentParser) -> None:
    """Add common args for CSIRO contest subparsers."""
    add_common_contest_args(parser)
    parser.add_argument(
        "--preprocessing", type=str, default="", help="Comma-separated preprocessing list"
    )
    parser.add_argument(
        "--data-augmentation", type=str, default="", help="Comma-separated augmentation list"
    )


def resolve_dataset_type(args: Any, default: str = "split") -> str:
    """Resolve dataset type from args or default."""
    return getattr(args, "dataset_type", default) or default
