"""Cross-validation workflow."""

import numpy as np

from pathlib import Path
from typing import Any, Dict, List, Optional

from sklearn.model_selection import KFold, StratifiedKFold

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import BasePipeline
from layers.layer_0_core.level_4 import EvaluatePipeline
from layers.layer_0_core.level_6 import PredictPipeline
from layers.layer_0_core.level_8 import TrainPipeline

_logger = get_logger(__name__)


class CrossValidateWorkflow(BasePipeline):
    """
    Workflow that performs k-fold cross-validation.

    Composes:
    - TrainPipeline: Train model for each fold
    - EvaluatePipeline: Evaluate each fold
    - Aggregates results across folds
    """

    DEFAULT_TABULAR_METRIC_KEY = 'f1_macro'

    def __init__(
        self,
        config: Any,
        model_type: str = 'vision',
        n_folds: int = 5,
        shuffle: bool = True,
        random_state: int = 42,
        primary_metric_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize cross-validation workflow.

        Args:
            config: Configuration object.
            model_type: Type of model ('vision' or 'tabular').
            n_folds: Number of CV folds (default: 5).
            shuffle: Whether to shuffle data before splitting (default: True).
            random_state: Random seed for reproducibility (default: 42).
            primary_metric_key: Key for tabular fold score in eval metrics (default: 'f1_macro').
            **kwargs: Additional parameters passed to train and evaluate pipelines.
        """
        super().__init__(config)
        self.kwargs = kwargs
        self.model_type = model_type
        self.n_folds = n_folds
        self.shuffle = shuffle
        self.random_state = random_state
        self.primary_metric_key = primary_metric_key or self.DEFAULT_TABULAR_METRIC_KEY
        self.fold_results = []
        self.cv_metrics = None

    def setup(self) -> None:
        """Setup cross-validation workflow."""
        _logger.info("🔧 Setting up cross-validation workflow...")

        # Validate required data
        if self.model_type == 'vision':
            if 'train_data' not in self.kwargs:
                raise ValueError("train_data required for vision cross-validation")
        elif self.model_type == 'tabular':
            if 'X' not in self.kwargs or 'y' not in self.kwargs:
                raise ValueError("X and y required for tabular cross-validation")

        _logger.info(f"  CV Configuration: {self.n_folds} folds, shuffle={self.shuffle}")
        _logger.info("✅ Cross-validation workflow setup complete")

    def execute(self) -> Dict[str, Any]:
        """
        Execute cross-validation workflow.

        Returns:
            Dictionary with CV results:
            - 'success': bool
            - 'cv_score': float (mean score across folds)
            - 'fold_scores': list (scores for each fold)
            - 'fold_results': list (detailed results for each fold)
        """
        _logger.info("🚀 Starting cross-validation workflow...")

        if self.model_type == 'vision':
            return self._cv_vision()
        elif self.model_type == 'tabular':
            return self._cv_tabular()
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")

    def _cv_vision(self) -> Dict[str, Any]:
        """Perform CV for vision models."""

        train_data = self.kwargs['train_data']

        # Create CV splits
        # For vision, we typically split by image_id to avoid data leakage
        unique_ids = train_data['image_id'].unique() if 'image_id' in train_data.columns else train_data.index

        kf = KFold(n_splits=self.n_folds, shuffle=self.shuffle, random_state=self.random_state)

        fold_scores = []

        for fold_idx, (train_idx, val_idx) in enumerate(kf.split(unique_ids)):
            _logger.info("=" * 60)
            _logger.info(f"FOLD {fold_idx + 1}/{self.n_folds}")
            _logger.info("=" * 60)

            # Split data
            train_ids = unique_ids[train_idx]
            val_ids = unique_ids[val_idx]

            train_fold = train_data[train_data['image_id'].isin(train_ids)] if 'image_id' in train_data.columns else train_data.iloc[train_idx]
            val_fold = train_data[train_data['image_id'].isin(val_ids)] if 'image_id' in train_data.columns else train_data.iloc[val_idx]

            # Train
            train_pipeline = TrainPipeline(
                config=self.config,
                model_type='vision',
                train_data=train_fold,
                val_data=val_fold,
                checkpoint_dir=str(Path(self.config.paths.output_dir) / 'checkpoints' / f'fold_{fold_idx}'),
                **{k: v for k, v in self.kwargs.items() if k not in ['train_data']}
            )

            train_results = train_pipeline.run()

            # Evaluate (would need to generate predictions first, then evaluate)
            # For now, use training metrics
            fold_score = train_results['metrics'].get('best_score', 0.0)
            fold_scores.append(fold_score)

            self.fold_results.append({
                'fold': fold_idx,
                'train_results': train_results,
                'score': fold_score
            })

        return self._aggregate_cv_results(fold_scores)

    def _aggregate_cv_results(self, fold_scores: List[float]) -> Dict[str, Any]:
        """Aggregate fold scores and log summary."""
        cv_score = np.mean(fold_scores)
        cv_std = np.std(fold_scores)
        _logger.info("=" * 60)
        _logger.info("CROSS-VALIDATION RESULTS")
        _logger.info("=" * 60)
        _logger.info(f"  Mean CV Score: {cv_score:.4f} ± {cv_std:.4f}")
        _logger.info(f"  Fold Scores: {fold_scores}")
        return {
            'success': True,
            'cv_score': cv_score,
            'cv_std': cv_std,
            'fold_scores': fold_scores,
            'fold_results': self.fold_results
        }

    def _cv_tabular(self) -> Dict[str, Any]:
        """Perform CV for tabular models."""
        X = self.kwargs['X']
        y = self.kwargs['y']

        # Create CV splits
        if y.ndim == 1 or y.shape[1] == 1:
            # Single-label: use StratifiedKFold
            kf = StratifiedKFold(n_splits=self.n_folds, shuffle=self.shuffle, random_state=self.random_state)
            splits = kf.split(X, y.ravel() if y.ndim > 1 else y)
        else:
            # Multi-label: use KFold
            kf = KFold(n_splits=self.n_folds, shuffle=self.shuffle, random_state=self.random_state)
            splits = kf.split(X)

        fold_scores = []

        for fold_idx, (train_idx, val_idx) in enumerate(splits):
            _logger.info("=" * 60)
            _logger.info(f"FOLD {fold_idx + 1}/{self.n_folds}")
            _logger.info("=" * 60)

            # Split data
            X_train_fold = X[train_idx]
            X_val_fold = X[val_idx]
            y_train_fold = y[train_idx]
            y_val_fold = y[val_idx]

            # Train
            train_pipeline = TrainPipeline(
                config=self.config,
                model_type='tabular',
                X_train=X_train_fold,
                y_train=y_train_fold,
                **{k: v for k, v in self.kwargs.items() if k not in ['X', 'y']}
            )

            train_results = train_pipeline.run()

            # Predict
            predict_pipeline = PredictPipeline(
                config=self.config,
                model_path=train_results['model_path'],
                model_type='tabular',
                X_test=X_val_fold
            )

            predict_results = predict_pipeline.run()

            # Evaluate
            evaluate_pipeline = EvaluatePipeline(
                config=self.config,
                predictions=predict_results['predictions'],
                ground_truth=y_val_fold,
                model_type='tabular'
            )

            eval_results = evaluate_pipeline.run()

            fold_score = eval_results['metrics'].get(self.primary_metric_key, 0.0)
            fold_scores.append(fold_score)

            self.fold_results.append({
                'fold': fold_idx,
                'train_results': train_results,
                'predict_results': predict_results,
                'eval_results': eval_results,
                'score': fold_score
            })

        return self._aggregate_cv_results(fold_scores)

    def cleanup(self) -> None:
        """Cleanup CV resources."""
        pass
