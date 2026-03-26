"""Per-target weighted ensemble: different weights for each target."""

import numpy as np

from typing import Dict, List, Optional

from level_0 import (
    get_logger,
    EnsemblingMethod,
    validate_predictions_list,
    get_shape_and_targets,
    combine_predictions_loop,
    combine_predictions_vectorized,
)

from level_2 import build_weight_matrix

logger = get_logger(__name__)


class PerTargetWeightedEnsemble(EnsemblingMethod):
    """Ensemble that applies different per-model weights per target column."""

    def __init__(
        self,
        per_target_weights: Dict[str, List[float]],
        target_names: Optional[List[str]] = None,
        use_vectorized: bool = True,
    ):
        """
        Initialize per-target weighted ensemble.

        Args:
            per_target_weights: Dict mapping target name to list of per-model weights.
            target_names: Optional ordered list of target names; must match prediction columns.
            use_vectorized: If True, use vectorized combination; else loop-based.
        """
        self.per_target_weights = per_target_weights
        self.target_names = target_names
        self.use_vectorized = use_vectorized

    def combine(
        self,
        predictions_list: List[np.ndarray],
        weights: Optional[List[float]] = None,
    ) -> np.ndarray:
        """Combine predictions using per-target weight matrix. Ignores weights arg."""
        validate_predictions_list(predictions_list)

        shape, num_targets = get_shape_and_targets(predictions_list)
        num_models = len(predictions_list)

        if self.target_names is not None:
            target_names = self.target_names

            if len(target_names) != num_targets:
                raise ValueError(
                    f"target_names length ({len(target_names)}) must match "
                    f"number of targets ({num_targets})"
                )
        else:
            target_names = [f"target_{i}" for i in range(num_targets)]

        weight_matrix = build_weight_matrix(
            self.per_target_weights,
            target_names,
            num_models,
        )

        if self.use_vectorized:
            result = combine_predictions_vectorized(
                predictions_list,
                weight_matrix,
            )
        else:
            result = np.zeros(shape, dtype=np.float32)
            result = combine_predictions_loop(
                predictions_list,
                weight_matrix,
                result,
            )

        logger.info("Combined predictions using per-target weighted ensemble")

        return result

    def get_name(self) -> str:
        """Return ensemble method identifier."""
        return "per_target_weighted"
