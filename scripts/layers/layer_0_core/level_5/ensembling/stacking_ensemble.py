"""Stacking ensemble implementation with OOF predictions and Ridge meta-model."""

import numpy as np

from pathlib import Path
from typing import Any, Dict, List, Tuple

from layers.layer_0_core.level_0 import get_logger
from level_2 import get_ridge, get_kfold
from level_3 import create_regression_model
from level_4 import load_pickle

logger = get_logger(__name__)


class StackingEnsemble:
    """
    Stacking ensemble using base models and a per-target Ridge meta-model.

    Stage 1 (base models): LGBM, XGBoost, Ridge generate predictions via
    out-of-fold (OOF) cross-validation.
    Stage 2 (meta-model): one Ridge regressor per target combines base predictions.
    """

    def __init__(
        self,
        model_paths: List[str],
        model_configs: List[Dict[str, Any]],
        feature_extraction_model_name: str,
        n_folds: int = 5,
        meta_model_alpha: float = 10.0,
        random_state: int = 42,
    ):
        """
        Initialise stacking ensemble.

        Args:
            model_paths: Paths to regression model directories (or .pkl files).
            model_configs: Metadata dicts for each base model (same order as model_paths).
            feature_extraction_model_name: Name of the upstream feature extraction model.
            n_folds: Number of folds for OOF prediction generation.
            meta_model_alpha: Ridge regularisation strength for the meta-model.
            random_state: Random seed for reproducibility.
        """
        self.model_paths = model_paths
        self.model_configs = model_configs
        self.feature_extraction_model_name = feature_extraction_model_name
        self.n_folds = n_folds
        self.meta_model_alpha = meta_model_alpha
        self.random_state = random_state

        self.models: List[Any] = []
        self.meta_models: Dict[int, Any] = {}
        self.model_names: List[str] = []

        self._load_models()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def _load_models(self) -> None:
        """Load all base regression models from disk."""
        logger.info(f"Loading {len(self.model_paths)} base models for stacking...")

        for idx, model_path in enumerate(self.model_paths):
            model_path_obj = Path(model_path)

            model_file = model_path_obj / 'regression_model.pkl'
            if not model_file.exists():
                if model_path_obj.suffix == '.pkl' and model_path_obj.exists():
                    model_file = model_path_obj
                else:
                    raise FileNotFoundError(f"Regression model not found: {model_path}")

            self.models.append(load_pickle(model_file))
            self.model_names.append(self._infer_model_name(idx, model_path))

            logger.info(
                f"  Loaded {self.model_names[-1]} "
                f"({idx + 1}/{len(self.model_paths)}): {model_file}"
            )

        logger.info(f"All {len(self.models)} base models loaded")

    def _infer_model_name(self, idx: int, model_path: str) -> str:
        """Infer a human-readable model name from config metadata or path string."""
        if idx < len(self.model_configs):
            regression_model_type = self.model_configs[idx].get('regression_model_type')
            if regression_model_type:
                return regression_model_type.lower()

        path_lower = str(model_path).lower()
        if 'lgbm' in path_lower:
            return 'lgbm'
        if 'xgboost' in path_lower or 'xgb' in path_lower:
            return 'xgb'
        if 'ridge' in path_lower:
            return 'ridge'
        return f"model_{idx + 1}"

    # ------------------------------------------------------------------
    # OOF generation
    # ------------------------------------------------------------------

    def generate_oof_predictions(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_test: np.ndarray,
    ) -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]:
        """
        Generate out-of-fold predictions over the training set and averaged
        test predictions.

        Args:
            X_train: Training features, shape (N_train, feat_dim).
            y_train: Training targets, shape (N_train, num_targets).
            X_test: Test features, shape (N_test, feat_dim).

        Returns:
            (oof_preds, test_preds) where each maps model_name -> ndarray.
        """
        logger.info(f"Generating OOF predictions ({self.n_folds}-fold CV)...")

        n_train, n_targets = X_train.shape[0], y_train.shape[1]
        n_test = X_test.shape[0]

        oof_preds = {name: np.zeros((n_train, n_targets)) for name in self.model_names}
        test_preds = {name: np.zeros((n_test, n_targets)) for name in self.model_names}

        KFold = get_kfold()
        kf = KFold(n_splits=self.n_folds, shuffle=True, random_state=self.random_state)

        for fold, (train_idx, val_idx) in enumerate(kf.split(X_train, y_train)):
            logger.info(f"  Fold {fold + 1}/{self.n_folds}")
            X_tr, X_val = X_train[train_idx], X_train[val_idx]
            y_tr = y_train[train_idx]

            for model_name, model in zip(self.model_names, self.models):
                fold_model = create_regression_model(
                    getattr(model, 'model_type', None) or 'lgbm',
                    **getattr(model, 'model_params', {}),
                )
                fold_model.fit(X_tr, y_tr)

                oof_preds[model_name][val_idx] = np.clip(
                    self._to_2d(fold_model.predict(X_val)), 0, None
                )
                test_preds[model_name] += np.clip(
                    self._to_2d(fold_model.predict(X_test)), 0, None
                ) / self.n_folds

        logger.info("OOF predictions generated successfully")
        return oof_preds, test_preds

    # ------------------------------------------------------------------
    # Meta-model
    # ------------------------------------------------------------------

    def fit_meta_models(
        self,
        oof_preds: Dict[str, np.ndarray],
        y_train: np.ndarray,
    ) -> None:
        """
        Fit one Ridge meta-model per target using OOF predictions as features.

        Args:
            oof_preds: Dict model_name -> OOF predictions (N_train, num_targets).
            y_train: True targets (N_train, num_targets).
        """
        logger.info("Fitting Ridge meta-models per target...")
        Ridge = get_ridge()

        for target_idx in range(y_train.shape[1]):
            X_meta = np.column_stack([
                oof_preds[name][:, target_idx] for name in self.model_names
            ])
            meta_model = Ridge(alpha=self.meta_model_alpha, random_state=self.random_state)
            meta_model.fit(X_meta, y_train[:, target_idx])
            self.meta_models[target_idx] = meta_model

            weights = ', '.join(
                f"{name}: {coef:.3f}"
                for name, coef in zip(self.model_names, meta_model.coef_)
            )
            logger.info(f"  Target {target_idx} -> {weights}")

        logger.info(f"Fitted {len(self.meta_models)} meta-models")

    def predict(self, test_preds: Dict[str, np.ndarray]) -> np.ndarray:
        """
        Produce final predictions by applying meta-models to base test predictions.

        Args:
            test_preds: Dict model_name -> test predictions (N_test, num_targets).

        Returns:
            Final predictions (N_test, num_targets), clipped to non-negative.
        """
        n_test = next(iter(test_preds.values())).shape[0]
        final = np.zeros((n_test, len(self.meta_models)))

        for target_idx, meta_model in self.meta_models.items():
            X_meta = np.column_stack([
                test_preds[name][:, target_idx] for name in self.model_names
            ])
            final[:, target_idx] = meta_model.predict(X_meta)

        return np.clip(final, 0, None)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _to_2d(arr: np.ndarray) -> np.ndarray:
        """Ensure a prediction array is 2D (N, num_targets)."""
        return arr.reshape(-1, 1) if arr.ndim == 1 else arr