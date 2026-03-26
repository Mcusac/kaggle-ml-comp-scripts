"""Abstract base class for ensemble combination methods."""

import numpy as np

from abc import ABC, abstractmethod
from typing import List, Optional


class EnsemblingMethod(ABC):
    """
    Abstract base class for ensemble combination methods.

    Defines the interface for combining predictions from multiple base models.
    Subclasses implement specific combination strategies.
    """

    @abstractmethod
    def combine(
        self,
        predictions_list: List[np.ndarray],
        weights: Optional[List[float]] = None,
    ) -> np.ndarray:
        """
        Combine predictions from multiple models.

        Args:
            predictions_list: List of prediction arrays, all same shape.
            weights: Optional weights for models (usage depends on method).

        Returns:
            Combined predictions array, shape (n_samples, n_targets).
        """
        ...

    @abstractmethod
    def get_name(self) -> str:
        """Return human-readable name of this ensemble method."""
        ...