"""Base classes and interfaces for metrics."""

import numpy as np

from abc import ABC, abstractmethod
from typing import Dict, Union

class Metric(ABC):
    """
    Abstract base class for all metrics.
    Provides a unified interface for metric calculation with consistent
    error handling and logging.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def calculate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        **kwargs,
    ) -> Union[float, Dict[str, float]]:
        """Calculate the metric."""
        ...

    def __call__(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        **kwargs,
    ) -> Union[float, Dict[str, float]]:
        return self.calculate(y_true, y_pred, **kwargs)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"