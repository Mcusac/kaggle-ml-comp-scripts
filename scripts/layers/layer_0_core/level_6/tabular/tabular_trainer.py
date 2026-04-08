"""Tabular model trainer. Uses level_0, level_2, level_5."""

import numpy as np
import pandas as pd

from typing import Dict, Any, Union, List

from level_0 import get_logger
from level_2 import get_train_test_split
from level_4 import calculate_metrics
from level_5 import BaseTabularModel

logger = get_logger(__name__)


class TabularTrainer:
    """
    Trainer for tabular models.

    Provides sklearn-style interface for training tabular models.
    """

    def __init__(
        self,
        model: BaseTabularModel,
        validation_split: float = 0.0,
        random_state: int = 42,
    ):
        """Initialize trainer."""
        self.model = model
        self.validation_split = validation_split
        self.random_state = random_state
        self.history: Dict[str, List[float]] = {}

    def fit(
        self,
        X: Union[np.ndarray, pd.DataFrame],
        y: Union[np.ndarray, pd.Series],
        **kwargs,
    ) -> Dict[str, Any]:
        """Train the model."""
        logger.info("Training tabular model...")

        if isinstance(X, pd.DataFrame):
            X = X.values
        if isinstance(y, pd.Series):
            y = y.values

        if self.validation_split > 0.0:
            train_test_split = get_train_test_split()
            X_train, X_val, y_train, y_val = train_test_split(
                X, y,
                test_size=self.validation_split,
                random_state=self.random_state,
            )

            self.model.fit(X_train, y_train, **kwargs)
            val_proba = self.model.predict_proba(X_val)
            val_pred = np.argmax(val_proba, axis=1)

            val_metrics = calculate_metrics(
                "classification", y_val, val_pred, y_pred_proba=val_proba
            )

            logger.info(f"Validation metrics: {val_metrics}")

            return {
                "success": True,
                "history": {"validation_metrics": val_metrics},
            }
        else:
            self.model.fit(X, y, **kwargs)

            return {
                "success": True,
                "history": {},
            }
