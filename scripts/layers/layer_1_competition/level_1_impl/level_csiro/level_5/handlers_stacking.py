"""Stacking command handlers for CSIRO CLI."""

import argparse
import json

from layers.layer_1_competition.level_0_infra.level_1 import resolve_data_root_from_args
from layers.layer_1_competition.level_1_impl.level_csiro.level_0 import resolve_dataset_type
from layers.layer_1_competition.level_1_impl.level_csiro.level_2 import (
    stacking_ensemble_pipeline,
    stacking_pipeline,
)
from layers.layer_1_competition.level_1_impl.level_csiro.level_4 import hybrid_stacking_pipeline


def handle_stacking(args: argparse.Namespace) -> None:
    """Handle stacking command."""
    data_root = resolve_data_root_from_args(args)
    stacking_config = json.loads(getattr(args, "stacking_config"))
    dataset_type = resolve_dataset_type(args)

    stacking_pipeline(
        data_root=data_root,
        stacking_config=stacking_config,
        dataset_type=dataset_type,
    )


def handle_stacking_ensemble(args: argparse.Namespace) -> None:
    """Handle stacking_ensemble command."""
    data_root = resolve_data_root_from_args(args)
    stacking_ensemble_config = json.loads(getattr(args, "stacking_ensemble_config"))
    dataset_type = resolve_dataset_type(args)

    stacking_ensemble_pipeline(
        data_root=data_root,
        stacking_ensemble_config=stacking_ensemble_config,
        dataset_type=dataset_type,
    )


def handle_hybrid_stacking(args: argparse.Namespace) -> None:
    """Handle hybrid_stacking command."""
    data_root = resolve_data_root_from_args(args)
    hybrid_stacking_config = json.loads(getattr(args, "hybrid_stacking_config"))
    dataset_type = resolve_dataset_type(args)

    hybrid_stacking_pipeline(
        data_root=data_root,
        hybrid_stacking_config=hybrid_stacking_config,
        dataset_type=dataset_type,
    )
