"""
Prediction combination helpers.
"""

import numpy as np

from typing import List

from level_0 import get_logger
from level_1 import ensure_positive_weights, normalize_weights
from level_2 import simple_average


logger = get_logger(__name__)


# =============================================================================
# COMBINATION HELPERS
# =============================================================================

def apply_weighted_combination(
    stacked: np.ndarray,
    normalized_weights: np.ndarray
) -> np.ndarray:
    """Apply weighted sum to stacked predictions."""
    weighted_sum = np.zeros_like(stacked[0], dtype=np.float32)

    for pred, weight in zip(stacked, normalized_weights):
        weighted_sum += pred * weight

    return weighted_sum


def combine_with_fallback(
    stacked: np.ndarray,
    weights_array: np.ndarray,
    predictions_list: List[np.ndarray],
    ensemble_name: str
) -> np.ndarray:
    """
    Combine predictions with normalization and fallback.
    """
    safe_weights = ensure_positive_weights(weights_array)

    normalized = normalize_weights(safe_weights)

    if normalized is None:
        logger.warning(
            f"{ensemble_name} failed: zero weight sum. "
            "Falling back to simple average."
        )
        return simple_average(predictions_list)

    combined = apply_weighted_combination(stacked, normalized)

    logger.info(
        f"Combined {len(predictions_list)} predictions using {ensemble_name}"
    )

    return combined