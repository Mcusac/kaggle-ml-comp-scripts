"""Tabular/sklearn regression models for multi-output regression."""

import numpy as np

from sklearn.multioutput import MultiOutputRegressor

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import check_array_finite

_logger = get_logger(__name__)


class BaseMultiOutputRegressionModel:
    """Base class for multi-output regression models."""

    def __init__(self, **params):
        """Initialize with default or provided parameters."""
        model_class = self._get_model_class()
        if model_class is None:
            raise RuntimeError(
                f"{self._get_model_name()} not available. Install required package."
            )
        default_params = self._get_default_params()
        default_params.update(params)
        self.model = MultiOutputRegressor(model_class(**default_params))
        _logger.info(
            f"Created {self._get_model_name()} regression model with MultiOutputRegressor"
        )

    def fit(self, X: np.ndarray, y: np.ndarray) -> "BaseMultiOutputRegressionModel":
        """
        Fit the model.

        Args:
            X: Feature array of shape (N, feat_dim).
            y: Target array of shape (N, num_targets).
        """
        check_array_finite(X, name="X")
        check_array_finite(y, name="y")
        _logger.info(
            f"Training {self._get_model_name()} regression model on {X.shape[0]} samples"
        )
        self.model.fit(X, y)
        _logger.info("Training complete")
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predict targets from features."""
        check_array_finite(X, name="X")
        return self._postprocess_predictions(self.model.predict(X))

    def _postprocess_predictions(self, predictions: np.ndarray) -> np.ndarray:
        """
        Hook for subclass output post-processing.

        Default implementation returns predictions unchanged. Subclasses may
        override to apply clipping, scaling, or domain-specific transforms.
        """
        return predictions

    def get_model(self) -> MultiOutputRegressor:
        """Return the underlying MultiOutputRegressor (for advanced usage)."""
        return self.model

    def _get_model_class(self):
        """Return the sklearn model class to instantiate. Subclasses must implement."""
        raise NotImplementedError

    def _get_default_params(self) -> dict:
        """Return default constructor parameters. Subclasses must implement."""
        raise NotImplementedError

    def _get_model_name(self) -> str:
        """Return model name for logging. Subclasses must implement."""
        raise NotImplementedError