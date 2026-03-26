"""Stacking ensemble via a learned meta-model.

Trains a meta-model on base model validation predictions to learn optimal
combination weights per target. Lives at level_4 (requires level_3).

Note: For equal-weight averaging use simple_average() from
level_2.ensemble_strategies.averaging_functions — do not duplicate it here.
"""

import numpy as np

from typing import Any, Dict, List, Optional

from level_0 import get_logger, DataValidationError, validate_targets
from level_1 import validate_paired_predictions
from level_3 import create_meta_model

logger = get_logger(__name__)

_VALID_META_MODEL_TYPES = {"ridge", "linear", "lasso"}


def _validate_meta_model_type(meta_model_type: str) -> None:
    """Raise DataValidationError if meta_model_type is not recognised."""
    if meta_model_type not in _VALID_META_MODEL_TYPES:
        raise DataValidationError(
            f"meta_model_type must be one of {_VALID_META_MODEL_TYPES}. "
            f"Got '{meta_model_type}'."
        )


def stacking_ensemble_with_validation(
    base_predictions_train: List[np.ndarray],
    base_predictions_val: List[np.ndarray],
    y_val: np.ndarray,
    meta_model_type: str = "ridge",
    meta_model_params: Optional[Dict[str, Any]] = None,
    random_state: int = 42,
) -> np.ndarray:
    """
    Stacking ensemble with a meta-model trained on validation data.

    Trains one independent meta-model per target variable. Each meta-model
    takes the stacked base model predictions as features and learns to predict
    the corresponding validation target.

    Process:
        1. Stack base model validation predictions into meta-features.
        2. For each target: train a fresh meta-model on (meta-features, target).
        3. Return ensemble predictions produced by the trained meta-models.

    Args:
        base_predictions_train: Base model predictions on the training set.
            Used for consistency validation only.
            Shape: list of (n_train_samples, n_targets).
        base_predictions_val: Base model predictions on the validation set.
            Used as meta-features for training.
            Shape: list of (n_val_samples, n_targets).
        y_val: Validation targets.
            Shape: (n_val_samples,) or (n_val_samples, n_targets).
        meta_model_type: One of 'ridge' (default), 'linear', 'lasso'.
        meta_model_params: Optional hyperparameters for the meta-model,
            e.g. {'alpha': 0.1} for ridge/lasso.
        random_state: Random seed for reproducibility (default 42).

    Returns:
        Ensemble predictions on the validation set.
        Shape: (n_val_samples, n_targets).

    Raises:
        DataValidationError: If any input validation check fails.

    Example:
        >>> base_train = [np.random.randn(10, 3), np.random.randn(10, 3)]
        >>> base_val   = [np.random.randn(10, 3), np.random.randn(10, 3)]
        >>> y_val      = np.random.randn(10, 3)
        >>> result = stacking_ensemble_with_validation(
        ...     base_train, base_val, y_val, meta_model_type='ridge'
        ... )
        >>> result.shape
        (10, 3)
    """
    _validate_meta_model_type(meta_model_type)

    n_base_models = validate_paired_predictions(base_predictions_train, base_predictions_val)
    n_val_samples, n_targets = base_predictions_val[0].shape
    validate_targets(y_val, n_val_samples, n_targets)

    logger.info(
        f"Stacking {n_base_models} base models with '{meta_model_type}' meta-model "
        f"({n_val_samples} val samples, {n_targets} targets)"
    )

    # Meta-features: (n_val_samples, n_base_models * n_targets)
    meta_features = np.hstack(base_predictions_val)
    ensemble_predictions = np.zeros((n_val_samples, n_targets))

    for target_idx in range(n_targets):
        # Columns for this target across all base models
        target_meta_features = meta_features[:, target_idx::n_targets]
        target_labels = y_val[:, target_idx] if y_val.ndim > 1 else y_val

        meta_model = create_meta_model(
            meta_model_type=meta_model_type,
            meta_model_params=meta_model_params,
            random_state=random_state,
        )
        meta_model.fit(target_meta_features, target_labels)
        ensemble_predictions[:, target_idx] = meta_model.predict(target_meta_features)

        logger.debug(
            f"Target {target_idx}: trained '{meta_model_type}' on "
            f"{n_val_samples} samples"
        )

    logger.info(f"Stacking complete: ensemble shape {ensemble_predictions.shape}")
    return ensemble_predictions