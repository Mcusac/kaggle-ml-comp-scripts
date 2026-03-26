"""Tree-based model wrappers for tabular classification."""

import numpy as np

from layers.layer_0_core.level_0 import get_logger
from level_2 import get_lgbm_classifier, get_xgb_classifier
from level_5 import BaseTabularModel

logger = get_logger(__name__)


class XGBoostModel(BaseTabularModel):
    """XGBoost classifier wrapped for BaseTabularModel interface."""

    def __init__(self, **kwargs):
        super().__init__(model_type="tree", **kwargs)
        XGBClassifier = get_xgb_classifier()
        default_params = {"random_state": 42, "verbosity": 0, "use_label_encoder": False}
        default_params.update(kwargs)
        self.model = XGBClassifier(**default_params)
        self.is_fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray, **kwargs) -> "XGBoostModel":
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
            "XGBoost",
        )

    def load(self, path: str) -> "XGBoostModel":
        data = self._load_from_pickle(path, "XGBoost")
        self.model = data["model"]
        self.is_fitted = data.get("is_fitted", True)
        return self


class LightGBMModel(BaseTabularModel):
    """LightGBM classifier wrapped for BaseTabularModel interface."""

    def __init__(self, **kwargs):
        super().__init__(model_type="tree", **kwargs)
        LGBMClassifier = get_lgbm_classifier()
        default_params = {"random_state": 42, "verbose": -1}
        default_params.update(kwargs)
        self.model = LGBMClassifier(**default_params)
        self.is_fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray, **kwargs) -> "LightGBMModel":
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
            "LightGBM",
        )

    def load(self, path: str) -> "LightGBMModel":
        data = self._load_from_pickle(path, "LightGBM")
        self.model = data["model"]
        self.is_fitted = data.get("is_fitted", True)
        return self
