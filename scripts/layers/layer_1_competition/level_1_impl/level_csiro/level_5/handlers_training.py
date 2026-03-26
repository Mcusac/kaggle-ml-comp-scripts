"""Training and export command handlers for CSIRO CLI."""

import argparse

from layers.layer_1_competition.level_0_infra.level_1 import resolve_data_root_from_args
from layers.layer_1_competition.level_0_infra.level_1 import export_model_pipeline

from layers.layer_1_competition.level_1_impl.level_csiro.level_0 import resolve_dataset_type
from layers.layer_1_competition.level_1_impl.level_csiro.level_2 import submit_best_variant_pipeline
from layers.layer_1_competition.level_1_impl.level_csiro.level_4 import get_grid_search_context
from layers.layer_1_competition.level_1_impl.level_csiro.level_6 import train_and_export_pipeline


def handle_submit_best(args: argparse.Namespace) -> None:
    """Handle submit_best command."""
    data_root = resolve_data_root_from_args(args)
    variant_id = getattr(args, "variant_id", None)
    results_file = getattr(args, "results_file", None)

    submit_best_variant_pipeline(
        data_root=data_root,
        variant_id=variant_id,
        results_file=results_file,
    )


def handle_export_model(args: argparse.Namespace) -> None:
    """Handle export_model command."""
    ctx = get_grid_search_context()
    data_root = resolve_data_root_from_args(args)
    results_file = getattr(args, "results_file", None)
    variant_id = getattr(args, "variant_id", None)
    best_variant_file = getattr(args, "best_variant_file", None)
    export_dir = getattr(args, "export_dir", None)

    export_model_pipeline(
        contest_context=ctx,
        data_root=data_root,
        results_file=results_file,
        variant_id=variant_id,
        best_variant_file=best_variant_file,
        export_dir=export_dir,
    )


def handle_train_and_export(args: argparse.Namespace) -> None:
    """Run train and export pipeline from CLI args."""
    data_root = resolve_data_root_from_args(args)
    dataset_type = resolve_dataset_type(args)

    train_and_export_pipeline(
        data_root=data_root,
        model=getattr(args, "model", None),
        results_file=getattr(args, "results_file", None),
        variant_id=getattr(args, "variant_id", None),
        export_dir=getattr(args, "export_dir", None),
        fresh_train=getattr(args, "fresh_train", False),
        export_only=getattr(args, "export_only", False),
        feature_extraction_mode=getattr(args, "feature_extraction_mode", False),
        feature_extraction_model=getattr(args, "feature_extraction_model", None),
        regression_model_type=getattr(args, "regression_model_type", None),
        regression_model_variant_id=getattr(args, "regression_model_variant_id", None),
        extract_features=getattr(args, "extract_features", True),
        data_manipulation_combo=getattr(args, "data_manipulation_combo", None),
        dataset_type=dataset_type,
    )
