"""Feature extraction setup and extraction-from-scratch for train-and-export pipeline."""

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import create_kfold_splits, get_device, cleanup_gpu_memory
from layers.layer_0_core.level_2 import save_features
from layers.layer_0_core.level_3 import create_train_dataloader

from layers.layer_1_competition.level_0_infra.level_4 import create_trainer

from layers.layer_1_competition.level_1_impl.level_csiro.level_0 import (
    aggregate_train_csv,
    calc_metric,
    get_model_image_size_for_extraction,
    resolve_feature_filename,
)
from layers.layer_1_competition.level_1_impl.level_csiro.level_2 import (
    initialize_working_metadata_files,
)

from layers.layer_1_competition.level_1_impl.level_csiro.level_3 import get_regression_variant_info


logger = get_logger(__name__)


def setup_feature_extraction_mode(
    feature_extraction_model: Optional[str],
    regression_model_type: Optional[str],
    regression_model_variant_id: Optional[str],
    data_manipulation_combo: Optional[str],
) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """
    Set up feature extraction mode and load regression variant info.

    Returns:
        Tuple of (regression_model_hyperparameters, regression_variant_info)
    """
    logger.info("=" * 60)
    logger.info("Loading regression model hyperparameters")
    logger.info("=" * 60)

    initialize_working_metadata_files(regression_model_type)

    feature_filename = resolve_feature_filename(
        feature_extraction_model=feature_extraction_model,
        data_manipulation_combo=data_manipulation_combo,
    )

    regression_model_hyperparameters = None
    regression_variant_info = None

    if not feature_filename:
        logger.warning(
            "Could not resolve feature_filename. "
            "Best variant selection requires feature_filename. "
            "Will use default hyperparameters."
        )
    else:
        try:
            regression_variant_info = get_regression_variant_info(
                regression_model_type=regression_model_type,
                feature_filename=feature_filename,
                variant_id=regression_model_variant_id,
            )

            regression_model_hyperparameters = regression_variant_info.get("hyperparameters", {})

            if regression_model_variant_id:
                logger.info("Loaded SPECIFIED regression variant: %s", regression_model_variant_id)
            else:
                logger.info(
                    "Loaded BEST regression variant: %s",
                    regression_variant_info.get("variant_id"),
                )
                cv_score = regression_variant_info.get("cv_score")
                if cv_score is not None:
                    logger.info("   (Highest CV score: %.4f)", cv_score)
                else:
                    logger.info(
                        "   (CV score: N/A - variant not yet trained for this feature file)"
                    )

            logger.info("   Variant ID: %s", regression_variant_info.get("variant_id"))
            cv_score = regression_variant_info.get("cv_score")
            if cv_score is not None:
                logger.info("   CV Score: %.4f", cv_score)
            else:
                logger.info("   CV Score: N/A (variant not yet trained for this feature file)")
            logger.info("   Hyperparameters: %s", regression_model_hyperparameters)
            logger.info("   Feature Filename: %s", regression_variant_info.get("feature_filename"))

        except (FileNotFoundError, ValueError) as e:
            logger.warning(
                "Could not load regression variant: %s. "
                "Will use default hyperparameters for regression model.",
                e,
            )
            regression_variant_info = None

    if not regression_model_hyperparameters:
        logger.warning(
            "No regression model hyperparameters loaded. "
            "Will use default hyperparameters for regression model."
        )

    logger.info("=" * 60 + "\n")
    return regression_model_hyperparameters, regression_variant_info


def extract_features_from_scratch(
    data_root: str,
    feature_extraction_model: str,
    feature_filename: str,
    dataset_type: str,
    contest_config: Any,
    regression_model_hyperparameters: Optional[Dict[str, Any]],
) -> Tuple[Any, Any, Any]:
    """Extract features from scratch and return features, targets, and fold assignments."""
    logger.info("=" * 60)
    logger.info("EXTRACTING FEATURES FROM SCRATCH")
    logger.info("=" * 60)

    device = get_device("auto")
    train_csv_path = Path(data_root) / "train.csv"
    if not train_csv_path.exists():
        raise FileNotFoundError(f"Train CSV not found: {train_csv_path}")

    logger.info("Loading train data from %s", train_csv_path)
    agg_train_df = aggregate_train_csv(train_csv_path)

    if "fold" not in agg_train_df.columns:
        agg_train_df = create_kfold_splits(
            agg_train_df,
            n_folds=5,
            shuffle=True,
            random_state=42,
        )

    feature_trainer = create_trainer(
        config=contest_config,
        device=device,
        regression_model_hyperparameters=regression_model_hyperparameters,
        metric_calculator=calc_metric,
    )

    image_size = get_model_image_size_for_extraction(feature_extraction_model)

    all_loader = create_train_dataloader(
        train_data=agg_train_df,
        data_root=data_root,
        config=contest_config,
        image_size=image_size,
        dataset_type=dataset_type,
        batch_size=32,
    )

    logger.info("Extracting features from all images...")
    all_features, all_targets = feature_trainer.extract_all_features(all_loader)
    fold_assignments = agg_train_df["fold"].values

    preprocessing_list = None
    if hasattr(contest_config, "data") and hasattr(contest_config.data, "preprocessing_list"):
        preprocessing_list = contest_config.data.preprocessing_list

    logger.info("Saving features to cache (filename: %s)...", feature_filename)
    save_features(
        all_features=all_features,
        all_targets=all_targets,
        fold_assignments=fold_assignments,
        filename=feature_filename,
        model_name=feature_extraction_model,
        dataset_type=dataset_type,
        image_size=image_size,
        preprocessing_list=preprocessing_list,
        use_input_dir=True,
    )

    del all_loader
    del feature_trainer
    cleanup_gpu_memory()

    logger.info("=" * 60)
    logger.info("FEATURE EXTRACTION COMPLETE")
    logger.info("=" * 60)
    logger.info("Extracted features shape: %s", all_features.shape)
    logger.info("Targets shape: %s", all_targets.shape)
    logger.info("Starting regression head training for all folds...")
    logger.info("=" * 60)

    return all_features, all_targets, fold_assignments
