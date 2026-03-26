"""Train and export pipeline for CSIRO contest.

Orchestrates training and export. Split into focused modules:
- model_resolution: Model ID, feature filename, image size
- config_setup: Contest config
- feature_extraction: Setup + extract from scratch
- regression_training: Fold-level and feature-extraction training
- e2e_training: End-to-end training
- export_ops: Export-only mode and export trained model
- result_persistence: Save gridsearch metadata
"""

from pathlib import Path
from typing import Optional

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_0_infra.level_1 import (
    get_best_model_path,
    get_data_root_path,
    get_output_path,
)

from layers.layer_1_competition.level_1_impl.level_csiro.level_0 import (
    export_trained_model,
    handle_export_only_mode,
    setup_contest_config,
)
from layers.layer_1_competition.level_1_impl.level_csiro.level_2 import train_end_to_end_model
from layers.layer_1_competition.level_1_impl.level_csiro.level_3 import save_regression_training_result
from layers.layer_1_competition.level_1_impl.level_csiro.level_4 import setup_feature_extraction_mode
from layers.layer_1_competition.level_1_impl.level_csiro.level_5 import train_feature_extraction_model

logger = get_logger(__name__)


def train_and_export_pipeline(
    data_root: Optional[str] = None,
    model: Optional[str] = None,
    results_file: Optional[str] = None,
    variant_id: Optional[str] = None,
    export_dir: Optional[str] = None,
    fresh_train: bool = False,
    export_only: bool = False,
    feature_extraction_mode: bool = False,
    feature_extraction_model: Optional[str] = None,
    regression_model_type: Optional[str] = None,
    regression_model_variant_id: Optional[str] = None,
    extract_features: bool = True,
    data_manipulation_combo: Optional[str] = None,
    dataset_type: str = "split",
) -> None:
    """
    Train model and export it for submission.

    Pipeline C: Orchestrates training and export operations.

    Modes:
    1. Export only (export_only=True):
       - Finds and exports existing model from training directory
       - No training performed (regardless of fresh_train setting)
    2. Train then export (export_only=False):
       - If fresh_train=True: Start fresh training
       - If fresh_train=False: Resume from checkpoints if incomplete folds exist
       - Exports the trained model

    Args:
        data_root: Data root directory (auto-detected if None)
        model: Model architecture name (e.g., 'efficientnet_b3')
        results_file: Optional path to grid search results.json to use best variant
        variant_id: Optional variant ID to use instead of best (for end-to-end)
        export_dir: Optional export directory (default: uses output path)
        fresh_train: If True, start fresh training. If False, resume from checkpoints.
        export_only: If True, skip training entirely and just export existing model.
        feature_extraction_mode: If True, use feature extraction + regression training
        feature_extraction_model: Model for feature extraction (e.g., 'dinov2_base')
        regression_model_type: Regression model type ('lgbm', 'xgboost', 'ridge')
        regression_model_variant_id: Optional regression model variant ID. If None, uses best variant.
        extract_features: Whether to extract features from scratch (True) or load from cache (False)
        data_manipulation_combo: Optional combo ID (e.g., 'combo_00', 'combo_63')
        dataset_type: Dataset type ('full' or 'split')
    """
    contest_config = setup_contest_config(
        feature_extraction_mode, feature_extraction_model, regression_model_type, dataset_type
    )

    if data_root is None:
        data_root = get_data_root_path()
    if export_dir is None:
        export_dir = str(get_best_model_path())

    logger.info("=" * 60)
    logger.info("TRAIN AND EXPORT PIPELINE")
    logger.info("=" * 60)
    logger.info("Data root: %s", data_root)
    logger.info("Dataset type: %s", dataset_type)
    logger.info("Mode: %s", "Export only" if export_only else "Train then export")
    logger.info("Feature extraction mode: %s", feature_extraction_mode)
    logger.info("Export directory: %s", export_dir)

    if export_only:
        handle_export_only_mode(
            model, export_dir, regression_model_type,
            feature_extraction_model, data_manipulation_combo, dataset_type,
        )
        return

    if fresh_train:
        logger.info("Train mode: Training fresh model (fresh_train=True)")
    else:
        logger.info("Train mode: Resuming from checkpoints (fresh_train=False)")

    training_model_dir = Path(get_output_path("best_model_training"))
    training_model_dir.mkdir(parents=True, exist_ok=True)

    regression_model_hyperparameters = None
    regression_variant_info = None

    if feature_extraction_mode and regression_model_type:
        regression_model_hyperparameters, regression_variant_info = setup_feature_extraction_mode(
            feature_extraction_model, regression_model_type,
            regression_model_variant_id, data_manipulation_combo,
        )

    logger.info("Starting training...")
    logger.info("Regression hyperparameters: %s", regression_model_hyperparameters)

    if feature_extraction_mode:
        export_variant_info = train_feature_extraction_model(
            data_root, feature_extraction_model, regression_model_type,
            regression_model_hyperparameters, data_manipulation_combo,
            extract_features, dataset_type, contest_config, training_model_dir,
        )

        if regression_variant_info:
            export_variant_info["variant_id"] = regression_variant_info.get("variant_id")
            export_variant_info["variant_index"] = regression_variant_info.get("variant_index", 0)

        save_regression_training_result(
            regression_model_type, export_variant_info, regression_model_hyperparameters
        )
    else:
        export_variant_info = train_end_to_end_model(
            data_root, model, variant_id, dataset_type
        )

    export_trained_model(
        training_model_dir, export_dir, regression_model_type,
        export_variant_info, regression_variant_info, regression_model_variant_id,
    )
