"""Regression ensemble OOF prediction generation."""

import numpy as np

from pathlib import Path
from typing import Any, Dict, List, Optional

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_2 import find_feature_cache, load_features
from layers.layer_0_core.level_4 import load_json

from layers.layer_1_competition.level_0_infra.level_2 import extract_test_features_from_model

from layers.layer_1_competition.level_1_impl.level_csiro.level_2 import generate_ensemble_oof_predictions

logger = get_logger(__name__)


def _find_feature_filename_from_ensembles(
    regression_ensembles: List[Dict[str, Any]]
) -> str:
    """Find feature filename from regression ensemble model metadata."""
    for ensemble_config in regression_ensembles:
        model_paths = ensemble_config.get('model_paths', [])
        if model_paths:
            first_model_path = model_paths[0]
            metadata_file = Path(first_model_path) / 'model_metadata.json'
            if metadata_file.exists():
                metadata = load_json(metadata_file)
                feature_filename = metadata.get('feature_filename')
                if feature_filename:
                    return feature_filename

    raise ValueError("Cannot determine feature filename from regression ensemble model metadata")


def load_features_for_regression(
    regression_ensembles: List[Dict[str, Any]],
    data_root: str,
    dataset_type: str,
    test_csv_path: Path,
    config: Any,
    data_schema: Any
) -> tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[np.ndarray]]:
    """Load training and test features for regression ensembles."""
    logger.info("Loading training features and targets for regression ensembles...")

    feature_filename = _find_feature_filename_from_ensembles(regression_ensembles)

    cache_path = find_feature_cache(feature_filename)
    if not cache_path:
        raise FileNotFoundError(f"Feature file not found: {feature_filename}")

    logger.info(f"Loading features from {cache_path}")
    all_features, all_targets_from_cache, fold_assignments, cache_metadata = load_features(cache_path)
    all_targets = all_targets_from_cache

    logger.info(f"Loaded features: {all_features.shape}, targets: {all_targets.shape}")

    test_features = extract_test_features_from_model(
        test_csv_path=test_csv_path,
        data_root=data_root,
        dataset_type=dataset_type,
        config=config,
        data_schema=data_schema,
        feature_extraction_model_name="dinov2_base",
    )

    return all_features, all_targets, test_features


def generate_regression_ensemble_oof_predictions(
    regression_ensembles: List[Dict[str, Any]],
    all_features: np.ndarray,
    all_targets: np.ndarray,
    test_features: np.ndarray,
    n_folds: int
) -> tuple[list, list]:
    """Generate OOF predictions from regression ensembles."""
    ensemble_oof_preds = []
    ensemble_test_preds = []

    logger.info("Generating regression ensemble-level OOF predictions...")
    for idx, ensemble_config in enumerate(regression_ensembles):
        logger.info(f"Processing regression ensemble {idx + 1}/{len(regression_ensembles)}...")
        oof_pred, test_pred = generate_ensemble_oof_predictions(
            ensemble_config=ensemble_config,
            all_features=all_features,
            all_targets=all_targets,
            test_features=test_features,
            n_folds=n_folds,
            random_state=42
        )
        ensemble_oof_preds.append(oof_pred)
        ensemble_test_preds.append(test_pred)
        logger.info(f"  Regression ensemble {idx + 1} OOF shape: {oof_pred.shape}, test shape: {test_pred.shape}")

    return ensemble_oof_preds, ensemble_test_preds
