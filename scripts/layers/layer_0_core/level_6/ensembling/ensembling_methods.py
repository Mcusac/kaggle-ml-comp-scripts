"""Averaging-based EnsemblingMethod implementations.

Wraps the functional averaging API in the EnsemblingMethod contract.
Requires level_5 (combine_with_fallback) so lives at level_6.

``weights`` in every class always means *model quality scores*, not
prediction-value transforms. See averaging_functions.py for the latter.

    SimpleAverageEnsemble      — equal weights
    WeightedAverageEnsemble    — score-proportional weights
    RankedAverageEnsemble      — weights from model score rank
    PercentileAverageEnsemble  — weights from model score percentile
    TargetSpecificEnsemble     — per-target model selection override
"""

import numpy as np

from typing import Dict, List, Optional

from level_0 import get_logger, EnsemblingMethod, calculate_percentile_weights
from level_1 import validate_predictions_for_ensemble
from level_2 import simple_average, model_rank_weights
from level_5 import combine_with_fallback

logger = get_logger(__name__)


class SimpleAverageEnsemble(EnsemblingMethod):
    """Equal-weight ensemble. Delegates to simple_average."""

    def combine(
        self,
        predictions_list: List[np.ndarray],
        weights: Optional[List[float]] = None,
    ) -> np.ndarray:
        """weights ignored -- all models contribute equally."""
        return simple_average(predictions_list)

    def get_name(self) -> str:
        return "simple_average"


class WeightedAverageEnsemble(EnsemblingMethod):
    """
    Score-proportional ensemble.

    weights are model quality scores (e.g. CV scores), normalised and
    passed directly to combine_with_fallback. Falls back to simple_average
    if normalisation fails.
    """

    def combine(
        self,
        predictions_list: List[np.ndarray],
        weights: List[float],
    ) -> np.ndarray:
        _, stacked = validate_predictions_for_ensemble(
            predictions_list, require_weights=True, weights=weights
        )
        return combine_with_fallback(
            stacked,
            np.array(weights, dtype=np.float32),
            predictions_list,
            ensemble_name="weighted average",
        )

    def get_name(self) -> str:
        return "weighted_average"


class RankedAverageEnsemble(EnsemblingMethod):
    """
    Model-rank-weighted ensemble.

    Converts model quality scores to ordinal rank weights (best model = N,
    next = N-1, ...). Emphasises relative ordering rather than absolute score
    magnitude -- useful when scores come from different metrics.
    """

    def combine(
        self,
        predictions_list: List[np.ndarray],
        weights: List[float],
    ) -> np.ndarray:
        _, stacked = validate_predictions_for_ensemble(
            predictions_list, require_weights=True, weights=weights
        )
        return combine_with_fallback(
            stacked,
            model_rank_weights(np.array(weights, dtype=np.float32)),
            predictions_list,
            ensemble_name="ranked average",
        )

    def get_name(self) -> str:
        return "ranked_average"


class PercentileAverageEnsemble(EnsemblingMethod):
    """
    Model-score-percentile-weighted ensemble.

    Converts model quality scores to empirical CDF values. Falls back to
    simple_average when all scores are identical.
    """

    def combine(
        self,
        predictions_list: List[np.ndarray],
        weights: List[float],
    ) -> np.ndarray:
        _, stacked = validate_predictions_for_ensemble(
            predictions_list, require_weights=True, weights=weights
        )
        percentile_weights = calculate_percentile_weights(np.array(weights, dtype=np.float32))
        if np.all(percentile_weights == percentile_weights[0]):
            logger.info("PercentileAverageEnsemble: all scores identical, falling back to simple average.")
            return simple_average(predictions_list)
        return combine_with_fallback(
            stacked, percentile_weights, predictions_list, ensemble_name="percentile average"
        )

    def get_name(self) -> str:
        return "percentile_average"


class TargetSpecificEnsemble(EnsemblingMethod):
    """
    Target-specific ensemble: use different models for different targets.

    Allows selecting which base model to use (or contribute most) for each
    target variable. Useful when different models excel at predicting
    different variables.

    Combines:
    1. Base ensemble method to get initial predictions for all targets
    2. Override selected targets with predictions from specific models

    The target_selection parameter uses target names (strings) as keys.
    These names are used to map to column indices in the prediction arrays.

    Use when:
    - Different base models are known to be better for different targets
    - You want to cherry-pick best predictions per target
    - You have domain knowledge about which model fits which target

    Args:
        target_selection: Dict mapping target name to model index.
                         Example: {'target_A': 0, 'target_B': 2}
        target_names: List of target names corresponding to columns in predictions.
                     If None, falls back to sequential naming (target_0, target_1, ...).
                     If list, must match number of targets in predictions.
        base_method: Base ensemble method for non-overridden targets.
                    Defaults to WeightedAverageEnsemble if None.

    Example:
        >>> selection = {'output_A': 0, 'output_B': 2}
        >>> names = ['output_A', 'output_B', 'output_C']
        >>> ensemble = TargetSpecificEnsemble(selection, target_names=names)
        >>> result = ensemble.combine(predictions, weights=scores)
    """

    def __init__(
        self,
        target_selection: Dict[str, int],
        target_names: Optional[List[str]] = None,
        base_method: Optional[EnsemblingMethod] = None,
    ):
        """
        Initialize target-specific ensemble.

        Args:
            target_selection: Mapping of target name to base model index.
            target_names: Names of targets (in order). If None, uses sequential naming.
            base_method: Ensemble method for non-overridden targets.
                        Defaults to WeightedAverageEnsemble if None.
        """
        self.target_selection = target_selection
        self.target_names = target_names
        self.base_method = base_method or WeightedAverageEnsemble()

    def combine(
        self,
        predictions_list: List[np.ndarray],
        weights: Optional[List[float]] = None,
    ) -> np.ndarray:
        """
        Combine predictions with target-specific model selection.

        Args:
            predictions_list: List of prediction arrays.
            weights: Weights for base ensemble method.

        Returns:
            Predictions with specified targets replaced by selected models.
        """
        shape = predictions_list[0].shape
        num_targets = shape[1] if len(shape) > 1 else 1

        if self.target_names is not None:
            target_names = self.target_names
            if len(target_names) != num_targets:
                raise ValueError(
                    f"target_names length ({len(target_names)}) must match "
                    f"number of targets ({num_targets})"
                )
        else:
            target_names = [f"target_{i}" for i in range(num_targets)]

        result = self.base_method.combine(predictions_list, weights)

        for target_name, model_idx in self.target_selection.items():
            if target_name not in target_names:
                logger.warning(
                    "Target '%s' not found in predictions, skipping",
                    target_name,
                )
                continue

            target_col = target_names.index(target_name)

            if model_idx < 0 or model_idx >= len(predictions_list):
                logger.warning(
                    "Model index %s out of range for target '%s', skipping",
                    model_idx,
                    target_name,
                )
                continue

            result[:, target_col] = predictions_list[model_idx][:, target_col]
            logger.info("Target '%s': using model %s", target_name, model_idx)

        logger.info(
            "Combined %s predictions using target-specific ensemble",
            len(predictions_list),
        )
        return result

    def get_name(self) -> str:
        return "target_specific"
