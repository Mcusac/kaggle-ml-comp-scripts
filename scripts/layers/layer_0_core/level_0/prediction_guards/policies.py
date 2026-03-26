"""Reusable prediction policy mixins for regression models."""

import numpy as np


class NonNegativePredictionMixin:
    """
    Mixin that enforces non-negative regression outputs.

    Use for targets that must be >= 0 (e.g., biomass, counts).
    """

    def _postprocess_predictions(self, predictions: np.ndarray) -> np.ndarray:
        """Clip predictions to non-negative values."""
        return np.clip(predictions, 0, None)
