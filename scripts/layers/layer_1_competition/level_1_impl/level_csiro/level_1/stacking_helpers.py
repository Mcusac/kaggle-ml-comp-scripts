"""Helper functions for stacking pipeline."""

import numpy as np

from pathlib import Path
from typing import Dict, Any, List, Tuple

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import get_model_name_from_model_id, parse_feature_filename
from layers.layer_0_core.level_2 import find_feature_cache, load_features
from layers.layer_0_core.level_4 import load_json
from layers.layer_0_core.level_5 import StackingEnsemble

from layers.layer_1_competition.level_1_impl.level_csiro.level_0 import calc_metric

logger = get_logger(__name__)


def load_model_metadata(model_paths: List[str]) -> Tuple[List[Dict[str, Any]], str]:
    """Load metadata from model paths and extract feature extraction model name."""

    default_model = 'dinov2_base'

    model_configs = []
    feature_extraction_model_name = None

    for model_path in model_paths:
        metadata_file = Path(model_path) / 'model_metadata.json'
        if not metadata_file.exists():
            if Path(model_path).suffix == '.pkl':
                metadata_file = Path(model_path).parent / 'model_metadata.json'

        if metadata_file.exists():
            metadata = load_json(metadata_file)
            model_configs.append(metadata)

            if feature_extraction_model_name is None:
                feature_filename = metadata.get('feature_filename')
                if feature_filename:
                    try:
                        model_id, _ = parse_feature_filename(feature_filename)
                        feature_extraction_model_name = get_model_name_from_model_id(model_id) or default_model
                    except Exception:
                        feature_extraction_model_name = default_model
        else:
            model_configs.append({})

    if not feature_extraction_model_name:
        feature_extraction_model_name = default_model

    return model_configs, feature_extraction_model_name


def load_training_features(
    model_configs: List[Dict[str, Any]],
    feature_extraction_model_name: str
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Dict[str, Any]]:
    """Load training features and targets from feature cache."""
    logger.info("Loading training features and targets...")

    feature_filename = None
    if model_configs and model_configs[0].get('feature_filename'):
        feature_filename = model_configs[0]['feature_filename']
    else:
        raise ValueError("Cannot determine feature filename from model metadata")


    cache_path = find_feature_cache(feature_filename)
    if not cache_path:
        raise FileNotFoundError(f"Feature file not found: {feature_filename}")

    logger.info(f"Loading features from {cache_path}")
    all_features, all_targets_from_cache, fold_assignments, cache_metadata = load_features(cache_path)
    all_targets = all_targets_from_cache

    logger.info(f"Loaded features: {all_features.shape}, targets: {all_targets.shape}")

    return all_features, all_targets, fold_assignments, cache_metadata


def create_and_train_stacking_ensemble(
    model_paths: List[str],
    model_configs: List[Dict[str, Any]],
    feature_extraction_model_name: str,
    all_features: np.ndarray,
    all_targets: np.ndarray,
    test_features: np.ndarray,
    n_folds: int,
    meta_model_alpha: float,
    config
) -> Tuple[np.ndarray, float]:
    """Create stacking ensemble, generate OOF predictions, train meta-models, and get final predictions."""
    logger.info(f"Creating stacking ensemble with {len(model_paths)} base models...")

    stacking = StackingEnsemble(
        model_paths=model_paths,
        model_configs=model_configs,
        feature_extraction_model_name=feature_extraction_model_name,
        n_folds=n_folds,
        meta_model_alpha=meta_model_alpha
    )

    logger.info("Generating out-of-fold predictions...")
    oof_preds, test_preds = stacking.generate_oof_predictions(
        X_train=all_features,
        y_train=all_targets,
        X_test=test_features
    )

    logger.info("Training meta-models...")
    stacking.fit_meta_models(oof_preds, all_targets)

    oof_combined = stacking.predict(oof_preds)
    oof_score, _ = calc_metric(oof_combined, all_targets, config=config)
    logger.info(f"Stacking OOF Score: {oof_score:.4f}")

    logger.info("Generating final test predictions...")
    final_predictions = stacking.predict(test_preds)
    logger.info(f"Final predictions shape: {final_predictions.shape}")

    return final_predictions, oof_score
