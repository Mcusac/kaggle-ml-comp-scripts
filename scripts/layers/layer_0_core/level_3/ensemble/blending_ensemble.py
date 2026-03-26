"""Blending ensemble: combine predictions with optional learned weights."""

import numpy as np

from scipy.optimize import minimize  # no project-level lazy loader for scipy
from typing import List, Optional

from level_0 import get_logger
from level_2 import (
    get_ridge,
    get_linear_regression,
    weighted_average,
    geometric_mean,
    power_average,
)

logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Shape alignment
# ---------------------------------------------------------------------------

def _align_predictions(
    predictions_list: List[np.ndarray],
    padding_strategy: str = 'zeros',
) -> List[np.ndarray]:
    """
    Pad all arrays in predictions_list to the element-wise maximum shape.

    Args:
        predictions_list: Prediction arrays that may differ in shape.
        padding_strategy: How to fill the padded region ('zeros', 'mean', 'noise').

    Returns:
        New list where every array shares the same maximum shape.
    """
    if not predictions_list:
        return predictions_list

    max_dims = list(predictions_list[0].shape)
    for pred in predictions_list[1:]:
        for i, dim in enumerate(pred.shape):
            if i < len(max_dims):
                max_dims[i] = max(max_dims[i], dim)
            else:
                max_dims.append(dim)

    aligned = [
        _pad_prediction(pred, tuple(max_dims), padding_strategy)
        if pred.shape != tuple(max_dims) else pred
        for pred in predictions_list
    ]

    logger.info(
        f"Aligned {len(predictions_list)} predictions to shape {tuple(max_dims)} "
        f"(padding: {padding_strategy})"
    )
    return aligned


def _pad_prediction(
    pred: np.ndarray,
    target_shape: tuple,
    method: str = 'zeros',
) -> np.ndarray:
    """
    Pad pred to target_shape using the specified fill method.

    Args:
        pred: Array to pad. Every dimension must be <= the corresponding target.
        target_shape: Shape of the returned array.
        method: Fill strategy for the padded region ('zeros', 'mean', 'noise').

    Returns:
        Padded array of shape target_shape.

    Raises:
        ValueError: If any source dimension exceeds the target, or method is unknown.
    """
    if pred.shape == target_shape:
        return pred

    for i, (current, target) in enumerate(zip(pred.shape, target_shape)):
        if current > target:
            raise ValueError(
                f"Cannot pad dimension {i}: source size {current} > target {target}."
            )

    slices = tuple(slice(0, s) for s in pred.shape)

    if method == 'zeros':
        padded = np.zeros(target_shape, dtype=pred.dtype)
        padded[slices] = pred
        return padded

    if method == 'mean':
        padded = np.full(target_shape, np.mean(pred), dtype=pred.dtype)
        padded[slices] = pred
        return padded

    if method == 'noise':
        noise = np.random.normal(np.mean(pred), np.std(pred) * 0.1, target_shape)
        noise[slices] = pred
        return noise.astype(pred.dtype)

    raise ValueError(
        f"Unknown padding method '{method}'. Expected: 'zeros', 'mean', 'noise'."
    )


# ---------------------------------------------------------------------------
# Blending
# ---------------------------------------------------------------------------

def blend_predictions(
    predictions_list: List[np.ndarray],
    weights: Optional[List[float]] = None,
    method: str = 'weighted_average',
    power: float = 1.5,
    padding_strategy: str = 'zeros',
) -> np.ndarray:
    """
    Combine a list of prediction arrays into one via the chosen method.

    Shape mismatches are resolved by padding smaller arrays to the maximum
    observed shape before combining.

    Args:
        predictions_list: Per-model prediction arrays (may differ in shape).
        weights: Per-model weights. Equal weights when None.
        method: Combination strategy:
            'weighted_average' — weighted mean (default).
            'geometric_mean'   — weighted geometric mean (log-space).
            'power_mean'       — power-mean with exponent `power`.
        power: Exponent for 'power_mean'. Ignored for other methods.
        padding_strategy: Padding fill for shape mismatches ('zeros', 'mean', 'noise').

    Returns:
        Combined prediction array.

    Raises:
        ValueError: If predictions_list is empty or method is unknown.
    """
    if not predictions_list:
        raise ValueError("predictions_list cannot be empty")

    shapes = [p.shape for p in predictions_list]
    if len(set(shapes)) > 1:
        logger.warning(f"Shape mismatch {shapes} — padding with strategy '{padding_strategy}'")
        predictions_list = _align_predictions(predictions_list, padding_strategy)

    if method == 'weighted_average':
        if weights is None:
            weights = [1.0 / len(predictions_list)] * len(predictions_list)
        return weighted_average(predictions_list, weights)

    if method == 'geometric_mean':
        return geometric_mean(predictions_list, weights=weights)

    if method == 'power_mean':
        return power_average(predictions_list, power=power, weights=weights)

    raise ValueError(
        f"Unknown method '{method}'. Expected: 'weighted_average', 'geometric_mean', 'power_mean'."
    )


# ---------------------------------------------------------------------------
# Weight learning
# ---------------------------------------------------------------------------

def learn_blending_weights(
    predictions_list: List[np.ndarray],
    y_val: np.ndarray,
    method: str = 'ridge',
    alpha: float = 1.0,
) -> List[float]:
    """
    Learn per-model blend weights by fitting to a held-out validation set.

    Args:
        predictions_list: Per-model validation predictions, each (n_samples, n_targets).
        y_val: Ground-truth validation targets, shape (n_samples, n_targets).
        method: Weight-learning strategy:
            'ridge'    — Ridge regression per target, averaged across targets.
            'linear'   — Unconstrained OLS per target, averaged across targets.
            'optimize' — Gradient-free MSE minimisation (L-BFGS-B).
        alpha: Ridge regularisation strength (ignored for 'linear' and 'optimize').

    Returns:
        Weights as a list of floats, normalised to sum to 1.0.

    Raises:
        ValueError: If predictions_list is empty or method is unknown.
    """
    if not predictions_list:
        raise ValueError("predictions_list cannot be empty")

    n_targets = predictions_list[0].shape[1]
    n_models = len(predictions_list)
    features = np.hstack(predictions_list)  # (n_samples, n_models * n_targets)

    if method in ('ridge', 'linear'):
        return _learn_weights_via_regression(
            features, y_val, n_targets, n_models, method, alpha
        )

    if method == 'optimize':
        return _learn_weights_via_optimisation(predictions_list, y_val, n_models)

    raise ValueError(
        f"Unknown method '{method}'. Expected: 'ridge', 'linear', 'optimize'."
    )


def _learn_weights_via_regression(
    features: np.ndarray,
    y_val: np.ndarray,
    n_targets: int,
    n_models: int,
    method: str,
    alpha: float,
) -> List[float]:
    """
    Fit one linear model per target, average coefficients, normalise.

    Args:
        features: Stacked prediction features (n_samples, n_models * n_targets).
        y_val: Validation targets (n_samples, n_targets).
        n_targets: Number of prediction targets.
        n_models: Number of base models.
        method: 'ridge' or 'linear'.
        alpha: Ridge regularisation strength.

    Returns:
        Normalised weight list of length n_models.
    """
    if method == 'ridge':
        Ridge = get_ridge()
        model = Ridge(alpha=alpha)
    else:
        LinearRegression = get_linear_regression()
        model = LinearRegression()

    all_weights = []
    for target_idx in range(n_targets):
        target_features = features[:, target_idx::n_models]
        target_y = y_val[:, target_idx] if y_val.ndim > 1 else y_val
        model.fit(target_features, target_y)
        all_weights.append(model.coef_)

    avg = np.mean(all_weights, axis=0)
    normalised = avg / avg.sum()
    logger.info(f"Learned blending weights ({method}): {normalised.tolist()}")
    return normalised.tolist()


def _learn_weights_via_optimisation(
    predictions_list: List[np.ndarray],
    y_val: np.ndarray,
    n_models: int,
) -> List[float]:
    """
    Minimise MSE on the validation set using L-BFGS-B.

    Args:
        predictions_list: Per-model validation predictions.
        y_val: Ground-truth validation targets.
        n_models: Number of base models.

    Returns:
        Normalised weight list of length n_models.
    """
    def _mse(w: np.ndarray) -> float:
        w = w / w.sum()
        blended = np.average(np.array(predictions_list), axis=0, weights=w)
        return float(np.mean((blended - y_val) ** 2))

    result = minimize(
        _mse,
        np.ones(n_models) / n_models,
        method='L-BFGS-B',
        bounds=[(0.0, 1.0)] * n_models,
    )
    normalised = result.x / result.x.sum()
    logger.info(f"Optimised blending weights: {normalised.tolist()}")
    return normalised.tolist()