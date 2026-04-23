"""Tabular model predictor."""

import numpy as np
import pandas as pd

from typing import Union, Optional

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_5 import BaseTabularModel

_logger = get_logger(__name__)


class TabularPredictor:
    """
    Predictor for tabular models.

    Handles prediction generation with optional threshold optimization.
    """

    def __init__(
        self,
        model: BaseTabularModel,
        threshold: float = 0.5,
    ):
        """
        Initialize predictor.

        Args:
            model: Trained tabular model.
            threshold: Prediction threshold for binary classification.
        """
        self.model = model
        self.threshold = threshold

    def predict(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        threshold: Optional[float] = None,
    ) -> np.ndarray:
        """
        Generate binary predictions.

        Args:
            X: Feature matrix.
            threshold: Optional threshold override.

        Returns:
            Binary predictions array.
        """
        if threshold is None:
            threshold = self.threshold

        if isinstance(X, pd.DataFrame):
            X = X.values

        return self.model.predict(X, threshold=threshold)

    def predict_proba(
        self,
        X: Union[np.ndarray, pd.DataFrame],
    ) -> np.ndarray:
        """
        Generate probability predictions.

        Args:
            X: Feature matrix.

        Returns:
            Probability predictions array.
        """
        if isinstance(X, pd.DataFrame):
            X = X.values

        return self.model.predict_proba(X)
