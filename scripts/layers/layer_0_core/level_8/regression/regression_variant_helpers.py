"""Helper functions for regression head variant execution."""

import numpy as np

from typing import Dict, Any

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import split_features_by_fold
from level_3 import create_regression_model
from level_7 import build_success_result

logger = get_logger(__name__)


def run_regression_cv_fold(
    fold: int,
    n_folds: int,
    all_features: np.ndarray,
    all_targets: np.ndarray,
    fold_assignments: np.ndarray,
    regression_model_type: str,
    hyperparameters: Dict[str, Any],
    config: Any,
    metric_calculator: Any,
) -> float:
    """
    Run a single CV fold for regression model.

    Args:
        fold: Fold number
        n_folds: Total number of folds
        all_features: All training features
        all_targets: All training targets
        fold_assignments: Fold assignments array
        regression_model_type: Type of regression model
        hyperparameters: Model hyperparameters
        config: Configuration object
        metric_calculator: Callable (predictions, targets, config) -> (weighted_r2, r2_per_target).
            Required. Must return weighted_r2 as first element.

    Returns:
        Fold score (weighted R²)
    """
    logger.info(f"Fold {fold+1}/{n_folds}")

    # Split features by fold
    train_features, val_features, train_targets, val_targets = split_features_by_fold(
        all_features, all_targets, fold_assignments, fold
    )

    # Create regression model with hyperparameters
    regression_model = create_regression_model(
        regression_model_type,
        **hyperparameters
    )

    # Train on training fold
    regression_model.fit(train_features, train_targets)

    val_predictions = regression_model.predict(val_features)
    weighted_r2, r2_scores = metric_calculator(val_predictions, val_targets, config=config)
    fold_score = weighted_r2

    logger.info(f"Fold {fold+1} score: {fold_score:.4f}")

    return fold_score


def create_regression_variant_result(
    variant_index: int,
    variant_id: str,
    cv_score: float,
    fold_scores: list,
    hyperparameters: Dict[str, Any],
    config: Any,
    feature_filename: str,
    regression_model_type: str
) -> Dict[str, Any]:
    """
    Create result dictionary for regression variant.

    Args:
        variant_index: Variant index
        variant_id: Variant ID
        cv_score: Average CV score
        fold_scores: List of fold scores
        hyperparameters: Hyperparameters used
        config: Configuration object
        feature_filename: Feature filename
        regression_model_type: Regression model type

    Returns:
        Result dictionary
    """

    return build_success_result(
        variant_index=variant_index,
        variant_id=variant_id,
        cv_score=cv_score,
        fold_scores=fold_scores,
        batch_size_used=None,
        batch_size_reduced=False,
        config=config,
        hyperparameters=hyperparameters,
        feature_filename=feature_filename,
        extra_fields={
            'regression_model_type': regression_model_type,
            'feature_filename': feature_filename,
        },
    )
