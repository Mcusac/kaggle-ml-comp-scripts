"""Regression ensemble: load regression models, predict, and combine predictions."""

import sys
import numpy as np

from pathlib import Path
from typing import Any, Dict, List, Optional

from level_0 import get_logger, EnsemblingMethod
from level_4 import load_pickle
from level_6 import SimpleAverageEnsemble
from level_7 import create_ensembling_method

logger = get_logger(__name__)

DEFAULT_FEATURE_EXTRACTION_MODEL = "dinov2_base"


class RegressionEnsemble:
    """Ensemble of regression models: load from paths, predict on features, combine."""

    def __init__(
        self,
        model_paths: List[str],
        model_configs: List[Dict[str, Any]],
        ensembling_method: EnsemblingMethod,
        feature_extraction_model_name: str,
        cv_scores: Optional[List[float]] = None,
        pickle_module_aliases: Optional[Dict[str, Any]] = None,
    ):
        if len(model_paths) != len(model_configs):
            raise ValueError(
                f"Number of model paths ({len(model_paths)}) must match "
                f"number of configs ({len(model_configs)})"
            )
        self.model_paths = model_paths
        self.model_configs = model_configs
        self.ensembling_method = ensembling_method
        self.feature_extraction_model_name = feature_extraction_model_name
        self.cv_scores = cv_scores
        self.pickle_module_aliases = pickle_module_aliases or {}
        self.models: List[Any] = []
        self._load_models()

    def _load_models(self) -> None:
        """Register any pickle module aliases then deserialize all models."""
        for alias, module in self.pickle_module_aliases.items():
            if alias not in sys.modules:
                sys.modules[alias] = module

        logger.info(f"Loading {len(self.model_paths)} regression models...")
        for idx, model_path in enumerate(self.model_paths):
            model_file = self._resolve_model_file(model_path)
            model = load_pickle(model_file)
            self.models.append(model)
            logger.info(f"  Loaded model {idx + 1}/{len(self.model_paths)}: {model_file}")
        logger.info(f"All {len(self.models)} models loaded successfully")

    @staticmethod
    def _resolve_model_file(model_path: str) -> Path:
        """Resolve a model path to its .pkl file, supporting both directory and direct paths."""
        path = Path(model_path)
        candidate = path / "regression_model.pkl"
        if candidate.exists():
            return candidate
        if path.suffix == ".pkl" and path.exists():
            return path
        raise FileNotFoundError(f"Regression model not found: {model_path}")

    def predict(
        self,
        features: np.ndarray,
        return_individual: bool = False,
    ) -> np.ndarray:
        """
        Predict on a 2-D feature array and combine predictions via the ensemble method.

        Args:
            features: Shape (n_samples, n_features).
            return_individual: If True, also return per-model predictions.

        Returns:
            Combined predictions array, clipped to non-negative values.
            If return_individual is True, returns (combined, list_of_individual).
        """
        if features.ndim != 2:
            raise ValueError(f"Features must be 2D array, got shape {features.shape}")

        all_predictions = []
        for model in self.models:
            preds = model.predict(features)
            if preds.ndim == 1:
                preds = preds.reshape(-1, 1)
            all_predictions.append(preds)

        weights = None
        method = self.ensembling_method
        method_name = method.get_name()
        if method_name in {"weighted_average", "ranked_average", "percentile_average"}:
            if self.cv_scores is not None:
                weights = self.cv_scores
            else:
                logger.warning(
                    f"Method '{method_name}' requires cv_scores but none were provided. "
                    "Falling back to simple average."
                )
                method = SimpleAverageEnsemble()

        combined = method.combine(all_predictions, weights)
        combined = np.clip(combined, 0, None)

        if return_individual:
            return combined, all_predictions
        return combined


def create_regression_ensemble_from_paths(
    model_paths: List[str],
    model_configs: List[Dict[str, Any]],
    method: str = "weighted_average",
    feature_extraction_model_name: Optional[str] = None,
    cv_scores: Optional[List[float]] = None,
    pickle_module_aliases: Optional[Dict[str, Any]] = None,
) -> RegressionEnsemble:
    """
    Create a RegressionEnsemble from model paths and metadata configs.

    Args:
        model_paths: Paths to model directories or .pkl files.
        model_configs: Per-model config dicts (must match model_paths length).
        method: Ensembling method name (e.g. 'weighted_average', 'simple_average').
        feature_extraction_model_name: Override for the feature extractor name.
        cv_scores: Per-model CV scores used by weighted/ranked/percentile methods.
        pickle_module_aliases: Optional dict of {alias: module} to register in
            sys.modules before unpickling (e.g. for models serialized under a
            different module name).

    Returns:
        Configured and loaded RegressionEnsemble.
    """
    if feature_extraction_model_name is None:
        feature_extraction_model_name = (
            model_configs[0].get("feature_filename") if model_configs else None
        ) or DEFAULT_FEATURE_EXTRACTION_MODEL

    ensembling_method = create_ensembling_method(method)
    return RegressionEnsemble(
        model_paths=model_paths,
        model_configs=model_configs,
        ensembling_method=ensembling_method,
        feature_extraction_model_name=feature_extraction_model_name,
        cv_scores=cv_scores,
        pickle_module_aliases=pickle_module_aliases,
    )
