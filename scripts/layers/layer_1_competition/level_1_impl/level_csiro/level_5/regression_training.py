"""Regression training (fold-level and feature-extraction mode) for train-and-export pipeline."""

import json
import pickle
import numpy as np

from pathlib import Path
from typing import Any, Dict, Optional
from sklearn.metrics import r2_score

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_2 import find_feature_cache, load_features
from layers.layer_0_core.level_3 import create_regression_model

from layers.layer_1_competition.level_1_impl.level_csiro.level_0 import resolve_feature_filename
from layers.layer_1_competition.level_1_impl.level_csiro.level_4 import extract_features_from_scratch

logger = get_logger(__name__)


def calculate_fold_score(
    val_predictions: np.ndarray,
    val_targets: np.ndarray,
    contest_config: Any,
) -> float:
    """Calculate weighted R2 score for a fold."""
    all_preds = contest_config.compute_derived_targets(val_predictions)
    all_targets_full = contest_config.compute_derived_targets(val_targets)

    target_weights = contest_config.target_weights
    target_order = contest_config.target_order

    r2_scores = []
    for i, target_name in enumerate(target_order):
        if i < all_targets_full.shape[1]:
            r2 = r2_score(all_targets_full[:, i], all_preds[:, i])
            r2_scores.append(r2)

    weighted_r2 = sum(
        target_weights.get(target_order[i], 0.0) * r2_scores[i]
        for i in range(min(len(r2_scores), len(target_order)))
    )

    return weighted_r2


def train_single_fold(
    fold: int,
    n_folds: int,
    all_features: np.ndarray,
    all_targets: np.ndarray,
    fold_assignments: np.ndarray,
    regression_model_type: str,
    regression_model_hyperparameters: Optional[Dict[str, Any]],
    contest_config: Any,
    training_model_dir: Path,
) -> float:
    """Train regression model for a single fold and return score."""
    logger.info("Training fold %s/%s", fold, n_folds - 1)
    fold_dir = training_model_dir / f"fold_{fold}"
    fold_dir.mkdir(parents=True, exist_ok=True)

    train_mask = fold_assignments != fold
    val_mask = fold_assignments == fold

    train_features = all_features[train_mask]
    val_features = all_features[val_mask]
    train_targets = all_targets[train_mask]
    val_targets = all_targets[val_mask]

    regression_model = create_regression_model(
        regression_model_type,
        **(regression_model_hyperparameters or {}),
    )
    regression_model.fit(train_features, train_targets)

    val_predictions = regression_model.predict(val_features)
    fold_score = calculate_fold_score(val_predictions, val_targets, contest_config)

    logger.info("Fold %s score: %.4f", fold, fold_score)

    model_path = fold_dir / "regression_model.pkl"
    with open(model_path, "wb") as f:
        pickle.dump(regression_model, f)

    metadata_path = fold_dir / "regression_model_info.json"
    with open(metadata_path, "w") as f:
        json.dump(
            {
                "best_score": float(fold_score),
                "val_score": float(fold_score),
                "cv_score": float(fold_score),
                "fold": fold,
            },
            f,
            indent=2,
        )

    return fold_score


def train_feature_extraction_model(
    data_root: str,
    feature_extraction_model: str,
    regression_model_type: str,
    regression_model_hyperparameters: Optional[Dict[str, Any]],
    data_manipulation_combo: Optional[str],
    extract_features: bool,
    dataset_type: str,
    contest_config: Any,
    training_model_dir: Path,
) -> Dict[str, Any]:
    """Train feature extraction + regression model."""
    feature_filename = resolve_feature_filename(feature_extraction_model, data_manipulation_combo)
    if not feature_filename:
        raise ValueError(
            "Could not resolve feature filename. "
            "Check feature_extraction_model and data_manipulation_combo."
        )

    cache_path = find_feature_cache(feature_filename)

    if cache_path and not extract_features:
        logger.info("Loading features from cache: %s", cache_path)
        all_features, all_targets, fold_assignments, cache_metadata = load_features(cache_path)
    else:
        all_features, all_targets, fold_assignments = extract_features_from_scratch(
            data_root,
            feature_extraction_model,
            feature_filename,
            dataset_type,
            contest_config,
            regression_model_hyperparameters,
        )

    n_folds = 5
    all_scores = []

    for fold in range(n_folds):
        fold_score = train_single_fold(
            fold,
            n_folds,
            all_features,
            all_targets,
            fold_assignments,
            regression_model_type,
            regression_model_hyperparameters,
            contest_config,
            training_model_dir,
        )
        all_scores.append(fold_score)

    cv_score = sum(all_scores) / len(all_scores)
    logger.info("Average CV score: %.4f", cv_score)

    best_fold = max(range(len(all_scores)), key=lambda i: all_scores[i])
    best_fold_score = all_scores[best_fold]

    logger.info("Best fold: %s (score: %.4f)", best_fold, best_fold_score)

    return {
        "variant_id": None,
        "variant_index": 0,
        "feature_filename": feature_filename,
        "cv_score": cv_score,
        "fold_scores": all_scores,
        "best_fold": best_fold,
        "best_fold_score": best_fold_score,
        "hyperparameters": regression_model_hyperparameters or {},
    }
