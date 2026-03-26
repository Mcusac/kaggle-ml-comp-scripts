"""Contest data schema abstract base class."""

import numpy as np

from abc import ABC, abstractmethod
from typing import List, Optional


class ContestDataSchema(ABC):
    """
    Abstract base class for contest-specific data schema.

    Defines CSV column names, sample ID format, and data validation.
    """

    @property
    @abstractmethod
    def sample_id_column(self) -> str:
        """
        Return name of the sample ID column.

        Returns:
            Column name for sample IDs
        """
        ...

    @property
    @abstractmethod
    def target_columns(self) -> List[str]:
        """
        Return list of target column names in CSV.

        Returns:
            List of target column names
        """
        ...

    @property
    def feature_columns(self) -> Optional[List[str]]:
        """
        Return list of feature column names, if applicable.

        Returns None for image competitions where features come from images.

        Returns:
            List of feature column names, or None
        """
        return None

    @abstractmethod
    def validate_sample_id(self, sample_id: str) -> bool:
        """
        Validate sample ID format.

        Args:
            sample_id: Sample ID to validate

        Returns:
            True if valid, False otherwise
        """
        ...

    def get_sample_weights(self, sample_ids: List[str]) -> Optional[np.ndarray]:
        """
        Get sample weights for training, if applicable.

        Args:
            sample_ids: List of sample IDs

        Returns:
            Array of weights, or None if no weighting
        """
        return None
