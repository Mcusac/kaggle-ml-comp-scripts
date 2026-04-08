"""Weight matrix builder for ensemble strategies."""

import numpy as np

from typing import Dict, List

from level_0 import get_logger
from level_1 import ensure_positive_weights

logger = get_logger(__name__)


def build_weight_matrix(
    per_target_weights: Dict[str, List[float]],
    target_names: List[str],
    num_models: int,
) -> np.ndarray:
    """
    Build normalized (targets, models) weight matrix.

    Args:
        per_target_weights: Mapping of target name to list of per-model weights.
            Targets absent from the mapping receive equal weights.
        target_names: Ordered list of target names defining row order.
        num_models: Number of models; must match each entry in per_target_weights.

    Returns:
        Float32 ndarray of shape (len(target_names), num_models) where each
        row sums to 1.0.

    Raises:
        ValueError: If any weight list length does not equal num_models.
    """

    num_targets = len(target_names)

    weight_matrix = np.zeros((num_targets, num_models), dtype=np.float32)

    for target_idx, target_name in enumerate(target_names):

        if target_name in per_target_weights:

            target_weights = np.asarray(
                per_target_weights[target_name],
                dtype=np.float32,
            )

            if len(target_weights) != num_models:
                raise ValueError(
                    f"Weights for target '{target_name}' must match "
                    f"number of models ({num_models})"
                )

            logger.debug(f"Target '{target_name}': using custom weights")

        else:
            target_weights = np.ones(num_models, dtype=np.float32)

            logger.debug(
                f"Target '{target_name}': no custom weights, using equal weights"
            )

        target_weights = ensure_positive_weights(target_weights)
        target_weights /= np.sum(target_weights)

        weight_matrix[target_idx] = target_weights

    return weight_matrix
