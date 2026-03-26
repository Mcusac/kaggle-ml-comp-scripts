"""Multi-variant regression training pipeline for CSIRO contest."""

import shutil

from pathlib import Path
from typing import List, Optional, Any

from layers.layer_0_core.level_0 import get_logger, ensure_dir
from layers.layer_0_core.level_1 import generate_feature_filename

from layers.layer_1_competition.level_0_infra.level_0 import get_model_id
from layers.layer_1_competition.level_0_infra.level_1 import get_contest

from layers.layer_1_competition.level_1_impl.level_csiro.level_1 import (
    apply_combo_to_config,
    get_variant_info_from_model_id,
)
from layers.layer_1_competition.level_1_impl.level_csiro.level_6 import train_and_export_pipeline

logger = get_logger(__name__)


def _validate_multi_variant_inputs(
    model_ids: Optional[List[str]],
    feature_extraction_model: Optional[str],
    regression_model_type: Optional[str]
) -> None:
    """Validate inputs for multi-variant training pipeline."""
    if not model_ids:
        raise ValueError("model_ids cannot be empty")
    if not feature_extraction_model:
        raise ValueError("feature_extraction_model is required")
    if not regression_model_type:
        raise ValueError("regression_model_type is required")


def _setup_multi_variant_config(
    config: Any,
    feature_extraction_model: str,
    regression_model_type: str,
    extract_features: bool,
    data_manipulation_combo: Optional[str]
) -> str:
    """Setup config and return feature filename."""
    # Set feature extraction mode in config
    if hasattr(config, 'model'):
        config.model.feature_extraction_mode = True
        config.model.regression_model_type = regression_model_type
        config.model.feature_extraction_model_name = feature_extraction_model
        config.model.extract_features = extract_features

    # Apply data manipulation combo if provided
    if data_manipulation_combo:
        try:
            apply_combo_to_config(config, data_manipulation_combo)
            logger.info(f"Applied data manipulation combo: {data_manipulation_combo}")
        except Exception as e:
            logger.warning(f"Could not load data manipulation combo {data_manipulation_combo}: {e}")

    # Generate feature filename
    model_id = get_model_id(feature_extraction_model)
    combo_id = data_manipulation_combo or 'combo_000'
    return generate_feature_filename(model_id, combo_id)


def _train_single_model_variant(
    model_id: str,
    model_idx: int,
    total_models: int,
    regression_model_type: str,
    feature_extraction_model: str,
    data_root: str,
    export_base: Path,
    paths: Any,
    fresh_train: bool,
    extract_features: bool,
    features_extracted: bool,
    dataset_type: str,
    **kwargs
) -> bool:
    """Train a single model variant and return whether features were extracted."""
    logger.info("\n" + "-" * 60)
    logger.info(f"Model {model_idx + 1}/{total_models}: model_id {model_id}")
    logger.info("-" * 60)

    try:
        # Get variant_id, feature_filename from model_id
        variant_id, model_feature_filename, cv_score = get_variant_info_from_model_id(
            regression_model_type, model_id
        )
        logger.info(f"  Model ID: {model_id}")
        logger.info(f"  Variant ID: {variant_id}")
        logger.info(f"  Feature filename: {model_feature_filename}")
        if cv_score is not None:
            logger.info(f"  CV score: {cv_score:.6f}")

        # Set up directories
        export_dir = export_base / f"best_model_{model_id}"
        ensure_dir(export_dir)

        model_dir = paths.get_models_base_dir() / f'model_{model_id}_training'
        ensure_dir(model_dir)

        if fresh_train and model_dir.exists():
            logger.info(f"  Deleting existing training directory for fresh training")
            shutil.rmtree(model_dir)

        # Determine if we should extract features
        should_extract = extract_features and not features_extracted

        if should_extract:
            logger.info(f"  Extracting features from scratch...")
        elif features_extracted:
            logger.info(f"  Reusing features from previous model...")
        else:
            logger.info(f"  Loading features from cache...")

        # Train and export
        train_and_export_pipeline(
            data_root=data_root,
            model=feature_extraction_model,
            results_file=None,
            variant_id=None,
            export_dir=str(export_dir),
            fresh_train=fresh_train and model_idx == 0,
            export_only=False,
            feature_extraction_mode=True,
            feature_extraction_model=feature_extraction_model,
            regression_model_type=regression_model_type,
            regression_model_variant_id=variant_id,
            extract_features=should_extract,
            dataset_type=dataset_type,
            **kwargs
        )

        logger.info(f"  Training and export complete for model_id {model_id}")
        logger.info(f"     Export directory: {export_dir}")

        return should_extract

    except Exception as e:
        logger.error(f"  Failed to train model_id {model_id}: {e}")
        logger.exception("Full error traceback:")
        return False


def multi_variant_regression_training_pipeline(
    data_root: Optional[str] = None,
    model_ids: Optional[List[str]] = None,
    feature_extraction_model: Optional[str] = None,
    regression_model_type: Optional[str] = None,
    data_manipulation_combo: Optional[str] = None,
    extract_features: bool = True,
    fresh_train: bool = False,
    dataset_type: str = 'split',
    **kwargs
) -> None:
    """
    Train and export multiple regression models, one per model_id.

    Pipeline flow:
    1. Extract features once (shared across all models)
    2. For each model_id:
       a. Get variant_id, feature_filename from model_id
       b. Load hyperparameters for that variant
       c. Train regression model
       d. Export to best_model_{model_id}/ folder

    Args:
        data_root: Data root directory (default: from contest paths).
        model_ids: List of model_id strings from gridsearch_metadata.json.
        feature_extraction_model: Model name for feature extraction.
        regression_model_type: Type of regression model ('lgbm', 'xgboost', 'ridge').
        data_manipulation_combo: Optional combo ID for data manipulation.
        extract_features: Whether to extract features from scratch.
        fresh_train: Whether to start fresh training.
        dataset_type: Dataset type ('full' or 'split').
        **kwargs: Additional arguments.
    """
    # Get contest
    contest = get_contest('csiro')
    paths = contest['paths']()
    config = contest['config']()

    # Resolve data root
    if data_root is None:
        data_root = str(paths.get_data_root())

    # Validate inputs
    _validate_multi_variant_inputs(model_ids, feature_extraction_model, regression_model_type)

    # Log pipeline start
    logger.info("=" * 60)
    logger.info("Multi-Variant Regression Training Pipeline")
    logger.info("=" * 60)
    logger.info(f"  Regression model type: {regression_model_type}")
    logger.info(f"  Feature extraction model: {feature_extraction_model}")
    logger.info(f"  Data manipulation combo: {data_manipulation_combo or 'combo_00 (default)'}")
    logger.info(f"  Model IDs to train: {model_ids}")
    logger.info(f"  Extract features: {extract_features}")
    logger.info(f"  Fresh train: {fresh_train}")

    # Setup config and get feature filename
    feature_filename = _setup_multi_variant_config(
        config, feature_extraction_model, regression_model_type,
        extract_features, data_manipulation_combo
    )

    # Base export directory
    export_base = paths.get_output_dir() / 'regression_training' / regression_model_type
    ensure_dir(export_base)

    # Track if features have been extracted
    features_extracted = False

    # Train each model
    logger.info("\n" + "=" * 60)
    logger.info("Training Regression Models per Model ID")
    logger.info("=" * 60)

    for model_idx, model_id in enumerate(model_ids):
        extracted = _train_single_model_variant(
            model_id, model_idx, len(model_ids), regression_model_type,
            feature_extraction_model, data_root, export_base, paths,
            fresh_train, extract_features, features_extracted, dataset_type, **kwargs
        )
        if extracted:
            features_extracted = True

    logger.info("\n" + "=" * 60)
    logger.info("Multi-Variant Regression Training Pipeline Complete")
    logger.info("=" * 60)
    logger.info(f"  Trained {len(model_ids)} models")
    logger.info(f"  Export base directory: {export_base}")
