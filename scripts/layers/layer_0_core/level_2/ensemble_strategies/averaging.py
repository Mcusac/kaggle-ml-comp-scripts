"""Averaging ensemble functions.

Pure functional API for combining prediction arrays. No dependency on
combine_with_fallback or EnsemblingMethod — lives at level_2.

    simple_average           — equal or explicitly weighted mean
    weighted_average         — alias: simple_average(weights=...)
    value_rank_average       — rank-transform prediction *values*, average, rescale
    value_percentile_average — Nth percentile *value* across models
    power_average            — power-mean
    geometric_mean           — weighted geometric mean (log-space)
    max_ensemble             — element-wise maximum across models
    merge_submissions        — alias: simple_average (competition helper)
"""

import numpy as np

from typing import List, Optional

from layers.layer_0_core.level_0 import get_logger, DataValidationError
from layers.layer_0_core.level_1 import validate_predictions_for_ensemble, normalize_weights

logger = get_logger(__name__)

_EPSILON = 1e-8


def model_rank_weights(scores: np.ndarray) -> np.ndarray:
    """Convert model quality scores to ordinal rank weights (best = N, worst = 1).

    Args:
        scores: Array of model quality scores.

    Returns:
        Array of rank weights where the highest-scoring model gets weight N.
    """
    n = len(scores)
    rank_weights = np.empty(n, dtype=np.float32)
    for rank, idx in enumerate(np.argsort(-scores), start=1):
        rank_weights[idx] = n - rank + 1
    return rank_weights


def simple_average(
    predictions_list: List[np.ndarray],
    weights: Optional[List[float]] = None,
) -> np.ndarray:
    """
    Equal or explicitly weighted mean of predictions.

    Args:
        predictions_list: List of prediction arrays (all same shape).
        weights: Optional per-model weights, normalised internally.
                 Defaults to equal weights.

    Returns:
        Averaged predictions array.

    Raises:
        DataValidationError: If weight count mismatches model count, or weights sum to zero.
    """
    _, stacked = validate_predictions_for_ensemble(predictions_list)

    if weights is None:
        w = np.ones(len(predictions_list))
    else:
        w = np.array(weights, dtype=float)
        if len(w) != len(predictions_list):
            raise DataValidationError(
                f"len(weights)={len(w)} != len(predictions_list)={len(predictions_list)}"
            )
    result = np.average(stacked, axis=0, weights=normalize_weights(w))
    logger.info(f"simple_average: {len(predictions_list)} models -> shape {result.shape}")
    return result


def weighted_average(
    predictions_list: List[np.ndarray],
    weights: List[float],
) -> np.ndarray:
    """Weighted mean -- explicit alias for simple_average(weights=...)."""
    return simple_average(predictions_list, weights=weights)


def value_rank_average(
    predictions_list: List[np.ndarray],
    weights: Optional[List[float]] = None,
) -> np.ndarray:
    """
    Rank-transform prediction *values*, average the ranks, rescale back.

    Each model's prediction array is independently converted to ordinal
    ranks, the ranks are averaged (optionally weighted), then rescaled
    linearly to [min_original, max_original].

    Args:
        predictions_list: List of prediction arrays (all same shape).
        weights: Optional per-model weights on the rank arrays.

    Returns:
        Rank-averaged predictions rescaled to the original value range.
    """
    _, stacked = validate_predictions_for_ensemble(predictions_list)

    ranked_array = np.array([
        pred.flatten().argsort().argsort().reshape(pred.shape).astype(float)
        for pred in predictions_list
    ])

    w = np.ones(len(predictions_list)) if weights is None else np.array(weights, dtype=float)
    averaged_ranks = np.average(ranked_array, axis=0, weights=normalize_weights(w))

    all_values = np.concatenate([p.flatten() for p in predictions_list])
    min_val, max_val = all_values.min(), all_values.max()
    max_rank = averaged_ranks.max()
    normalised = averaged_ranks / max_rank if max_rank > 0 else averaged_ranks
    result = min_val + normalised * (max_val - min_val)

    logger.info(f"value_rank_average: {len(predictions_list)} models -> shape {result.shape}")
    return result


def value_percentile_average(
    predictions_list: List[np.ndarray],
    percentile: float = 50.0,
) -> np.ndarray:
    """
    Nth percentile *value* across models at each prediction position.

    percentile=50 gives the median, which is robust to outlier models.

    Args:
        predictions_list: List of prediction arrays (all same shape).
        percentile: Value in [0, 100]. Default 50.0 (median).

    Returns:
        Predictions array of the same shape as each input.
    """
    _, stacked = validate_predictions_for_ensemble(predictions_list)
    result = np.percentile(stacked, percentile, axis=0)
    logger.info(
        f"value_percentile_average: {len(predictions_list)} models, "
        f"p={percentile} -> shape {result.shape}"
    )
    return result


def power_average(
    predictions_list: List[np.ndarray],
    power: float = 1.5,
    weights: Optional[List[float]] = None,
) -> np.ndarray:
    """
    Power-mean of predictions.

    Raises each value to ``power``, takes the weighted mean, applies the
    inverse power. Predictions are clamped to [eps, 1-eps].
    power=1 -> simple average. power>1 emphasises higher values.

    Args:
        predictions_list: List of prediction arrays (all same shape).
        power: Exponent > 0. Default 1.5.
        weights: Optional per-model weights, normalised internally.

    Returns:
        Power-averaged predictions array.

    Raises:
        DataValidationError: If power <= 0.
    """
    if power <= 0:
        raise DataValidationError(f"power must be > 0, got {power}.")

    _, stacked = validate_predictions_for_ensemble(predictions_list)
    stacked = np.clip(stacked, _EPSILON, 1.0 - _EPSILON)

    w = np.ones(len(predictions_list)) if weights is None else np.array(weights, dtype=float)
    result = np.power(
        np.average(np.power(stacked, power), axis=0, weights=normalize_weights(w)),
        1.0 / power,
    )
    logger.info(f"power_average: {len(predictions_list)} models, power={power} -> shape {result.shape}")
    return result


def geometric_mean(
    predictions_list: List[np.ndarray],
    weights: Optional[List[float]] = None,
) -> np.ndarray:
    """
    Weighted geometric mean of predictions (log-space average).

    Values are clamped to [eps, 1] before taking logarithms.
    Appropriate for probability-like predictions.

    Args:
        predictions_list: List of prediction arrays (all same shape).
        weights: Optional per-model weights, normalised internally.

    Returns:
        Geometric-mean predictions array.
    """
    _, stacked = validate_predictions_for_ensemble(predictions_list)
    stacked = np.clip(stacked, _EPSILON, 1.0)

    w = np.ones(len(predictions_list)) if weights is None else np.array(weights, dtype=float)
    result = np.exp(np.average(np.log(stacked), axis=0, weights=normalize_weights(w)))
    logger.info(f"geometric_mean: {len(predictions_list)} models -> shape {result.shape}")
    return result


def max_ensemble(predictions_list: List[np.ndarray]) -> np.ndarray:
    """
    Element-wise maximum across models.

    Args:
        predictions_list: List of prediction arrays (all same shape).

    Returns:
        Element-wise maximum predictions array.
    """
    _, stacked = validate_predictions_for_ensemble(predictions_list)
    result = np.max(stacked, axis=0)
    logger.info(f"max_ensemble: {len(predictions_list)} models -> shape {result.shape}")
    return result


def merge_submissions(
    predictions_list: List[np.ndarray],
    weights: Optional[List[float]] = None,
) -> np.ndarray:
    """Merge competition submissions -- alias for simple_average."""
    return simple_average(predictions_list, weights=weights)