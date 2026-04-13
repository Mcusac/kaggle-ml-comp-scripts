"""Contest post-processor abstract base class."""

import numpy as np

from abc import ABC, abstractmethod


class ContestPostProcessor(ABC):
    """
    Abstract base class for contest-specific post-processing.

    Defines constraint enforcement and prediction adjustments.
    """

    @abstractmethod
    def apply(self, predictions: np.ndarray) -> np.ndarray:
        """
        Apply post-processing to predictions.

        Args:
            predictions: Raw predictions array

        Returns:
            Post-processed predictions
        """
        ...

    def enforce_constraints(self, predictions: np.ndarray) -> np.ndarray:
        """
        Enforce domain-specific constraints on predictions.

        Default implementation returns predictions unchanged.
        Override for contest-specific constraints.

        Args:
            predictions: Predictions array

        Returns:
            Constrained predictions
        """
        return predictions

    def clip_values(
        self,
        predictions: np.ndarray,
        min_val: float = None,
        max_val: float = None
    ) -> np.ndarray:
        """
        Clip prediction values to valid range.

        Args:
            predictions: Predictions array
            min_val: Minimum allowed value
            max_val: Maximum allowed value

        Returns:
            Clipped predictions
        """
        if min_val is not None or max_val is not None:
            return np.clip(predictions, min_val, max_val)
        return predictions


class ClipRangePostProcessor(ContestPostProcessor):
    """
    Post-processor that clips predictions to a configurable min/max range.

    Use for competitions where outputs must lie within a valid interval
    (e.g., coordinate clipping for PDB format constraints).
    """

    def __init__(self, clip_min: float = 0.0, clip_max: float = 1.0):
        self.clip_min = float(clip_min)
        self.clip_max = float(clip_max)

    def apply(self, predictions: np.ndarray) -> np.ndarray:
        """Clip all values to [clip_min, clip_max]."""
        return self.clip_values(
            predictions, min_val=self.clip_min, max_val=self.clip_max
        )
