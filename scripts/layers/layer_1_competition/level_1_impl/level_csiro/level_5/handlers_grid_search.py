"""Grid search command handlers for CSIRO CLI."""

import argparse

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import normalize_search_type
from layers.layer_0_core.level_5 import cleanup_grid_search_checkpoints_retroactive
from layers.layer_0_core.level_9 import (
    regression_grid_search_pipeline,
    dataset_grid_search_pipeline,
    test_max_augmentation_pipeline,
)
from layers.layer_0_core.level_10 import hyperparameter_grid_search_pipeline

from layers.layer_1_competition.level_0_infra.level_1 import get_contest, resolve_data_root_from_args

from layers.layer_1_competition.level_1_impl.level_csiro.level_1 import train_pipeline
from layers.layer_1_competition.level_1_impl.level_csiro.level_4 import get_grid_search_context

_logger = get_logger(__name__)


def handle_dataset_grid_search(args: argparse.Namespace) -> None:
    """Handle dataset_grid_search command."""
    data_root = resolve_data_root_from_args(args)
    dataset_type = getattr(args, "dataset_type", "split") or "split"
    max_augmentation = getattr(args, "max_augmentation", False)
    ctx = get_grid_search_context()

    if max_augmentation:
        test_max_augmentation_pipeline(contest_context=ctx, data_root=data_root)
    else:
        dataset_grid_search_pipeline(
            contest_context=ctx,
            train_pipeline_fn=train_pipeline,
            data_root=data_root,
        )


def handle_hyperparameter_grid_search(args: argparse.Namespace) -> None:
    """Handle hyperparameter_grid_search command."""
    search_type_raw = getattr(args, "search_type", "thorough") or "thorough"
    search_type = normalize_search_type(search_type_raw)
    ctx = get_grid_search_context()

    hyperparameter_grid_search_pipeline(
        contest_context=ctx,
        train_pipeline_fn=train_pipeline,
        search_type=search_type,
    )


def handle_regression_grid_search(args: argparse.Namespace) -> None:
    """Handle regression_grid_search command."""
    ctx = get_grid_search_context()
    feature_filename = getattr(args, "feature_filename", None)
    if not feature_filename:
        raise ValueError("--feature-filename is required for regression_grid_search")

    regression_model_type = getattr(args, "regression_model_type", "lgbm") or "lgbm"
    search_type_raw = getattr(args, "search_type", "defaults") or "defaults"
    search_type = normalize_search_type(search_type_raw)
    data_root = resolve_data_root_from_args(args)

    regression_grid_search_pipeline(
        contest_context=ctx,
        config=None,
        feature_filename=feature_filename,
        regression_model_type=regression_model_type,
        search_type=search_type,
        data_root=data_root,
    )


def handle_cleanup_grid_search(args: argparse.Namespace) -> None:
    """Handle cleanup_grid_search command."""
    contest = get_contest("csiro")
    paths = contest["paths"]()

    model_dir = getattr(args, "model_dir", None) or str(paths.get_models_base_dir())
    results_file = getattr(args, "results_file", None) or str(
        paths.get_output_dir() / "dataset_grid_search" / "gridsearch_results.json"
    )
    keep_top = getattr(args, "keep_top", 20)

    _logger.info("Running retroactive cleanup:")
    _logger.info("  Model directory: %s", model_dir)
    _logger.info("  Results file: %s", results_file)
    _logger.info("  Keep top: %s variants", keep_top)

    variants_deleted, bytes_freed = cleanup_grid_search_checkpoints_retroactive(
        model_base_dir=model_dir,
        results_file=results_file,
        keep_top_n=keep_top,
    )

    _logger.info("Cleanup complete:")
    _logger.info("  Variants deleted: %s", variants_deleted)
    mb_freed = bytes_freed / (1024 * 1024)
    _logger.info("  Space freed: %.2f MB", mb_freed)
