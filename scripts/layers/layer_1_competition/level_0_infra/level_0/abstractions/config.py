"""Contest configuration abstract base class."""

import numpy as np

from abc import ABC, abstractmethod
from typing import Dict, List, Optional


class ContestConfig(ABC):
    """
    Abstract base class for contest-specific configuration.

    Defines target names, weights, and derived target computation logic.
    Each contest should implement this interface with its specific values.
    """

    @property
    @abstractmethod
    def target_weights(self) -> Dict[str, float]:
        """
        Return dictionary mapping target names to their weights for evaluation.

        Returns:
            Dict mapping target name -> weight
        """
        ...

    @property
    @abstractmethod
    def target_order(self) -> List[str]:
        """
        Return ordered list of all target names.

        Must match target_weights keys.

        Returns:
            List of target names in order
        """
        ...

    @property
    @abstractmethod
    def primary_targets(self) -> List[str]:
        """
        Return list of primary target names (model outputs).

        Returns:
            List of primary target names
        """
        ...

    @property
    @abstractmethod
    def derived_targets(self) -> List[str]:
        """
        Return list of derived target names (computed from primary targets).

        Returns:
            List of derived target names
        """
        ...

    @property
    def all_targets(self) -> List[str]:
        """
        Return list of all target names (primary + derived).

        Returns:
            List of all target names
        """
        return self.primary_targets + self.derived_targets

    @property
    def num_primary_targets(self) -> int:
        """
        Return number of primary targets (model output size).

        Returns:
            Number of primary targets
        """
        return len(self.primary_targets)

    @property
    def num_total_targets(self) -> int:
        """
        Return total number of targets (primary + derived).

        Returns:
            Total number of targets
        """
        return len(self.all_targets)

    def compute_derived_targets(self, predictions: np.ndarray) -> np.ndarray:
        """
        Compute derived target values from primary target values.

        Default: identity (no derived targets). Override in subclasses for
        contests that compute derived targets (e.g., GDM from primary biomass).

        Args:
            predictions: Array of shape (N, num_primary_targets)

        Returns:
            Array of shape (N, num_total_targets) with derived targets appended
        """
        return predictions

    @property
    def constraint_matrix(self) -> Optional[np.ndarray]:
        """
        Return constraint matrix for post-processing, or None if no constraints.

        Matrix should define constraints C @ Y = 0 where:
        - C is the constraint matrix (shape: (num_constraints, num_total_targets))
        - Y is the target values vector (shape: (num_total_targets,))

        Returns:
            Constraint matrix as numpy array, or None if no constraints
        """
        return None
