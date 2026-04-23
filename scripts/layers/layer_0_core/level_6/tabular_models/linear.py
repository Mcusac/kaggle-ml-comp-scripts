"""Linear model wrappers for tabular classification."""

import numpy as np

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_2 import get_logistic_regression, get_ridge_classifier
from layers.layer_0_core.level_5 import BaseTabularModel

_logger = get_logger(__name__)


class LogisticRegressionModel(BaseTabularModel):
    """Logistic regression classifier wrapped for BaseTabularModel interface."""

    def __init__(self, **kwargs):
        super().__init__(model_type="linear", **kwargs)
        LogisticRegression = get_logistic_regression()
        default_params = {"random_state": 42, "max_iter": 1000}
        default_params.update(kwargs)
        self.model = LogisticRegression(**default_params)
        self.is_fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray, **kwargs) -> "LogisticRegressionModel":
        if y.ndim == 1:
            y = y.reshape(-1, 1)
        self.model.fit(X, y, **kwargs)
        self.is_fitted = True
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        proba = self.model.predict_proba(X)
        if proba.ndim == 2 and proba.shape[1] == 2:
            proba = proba[:, 1:2]
        return np.asarray(proba, dtype=np.float32)

    def save(self, path: str) -> None:
        self._save_with_pickle(
            path,
            {"model": self.model, "is_fitted": self.is_fitted},
            "LogisticRegression",
        )

    def load(self, path: str) -> "LogisticRegressionModel":
        data = self._load_from_pickle(path, "LogisticRegression")
        self.model = data["model"]
        self.is_fitted = data.get("is_fitted", True)
        return self


class RidgeModel(BaseTabularModel):
    """Ridge classifier wrapped for BaseTabularModel interface."""

    def __init__(self, **kwargs):
        super().__init__(model_type="linear", **kwargs)
        RidgeClassifier = get_ridge_classifier()
        default_params = {"random_state": 42}
        default_params.update(kwargs)
        self.model = RidgeClassifier(**default_params)
        self.is_fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray, **kwargs) -> "RidgeModel":
        if y.ndim == 1:
            y = y.reshape(-1, 1)
        self.model.fit(X, y, **kwargs)
        self.is_fitted = True
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        decision = self.model.decision_function(X)
        if decision.ndim == 1:
            decision = decision.reshape(-1, 1)
        proba = 1.0 / (1.0 + np.exp(-np.clip(decision, -500, 500)))
        return np.asarray(proba, dtype=np.float32)

    def save(self, path: str) -> None:
        self._save_with_pickle(
            path,
            {"model": self.model, "is_fitted": self.is_fitted},
            "RidgeClassifier",
        )

    def load(self, path: str) -> "RidgeModel":
        data = self._load_from_pickle(path, "RidgeClassifier")
        self.model = data["model"]
        self.is_fitted = data.get("is_fitted", True)
        return self
