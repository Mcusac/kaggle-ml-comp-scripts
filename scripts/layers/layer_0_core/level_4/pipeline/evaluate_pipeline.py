"""Evaluation pipeline."""

import numpy as np
import json

from typing import Dict, Any, Optional
from pathlib import Path

from layers.layer_0_core.level_0 import ensure_dir, get_logger
from layers.layer_0_core.level_1 import BasePipeline, validate_config_section_exists
from level_3 import (
    calculate_regression_metrics,
    calculate_f1,
    calculate_precision,
    calculate_recall,
    calculate_roc_auc,
)

logger = get_logger(__name__)


class EvaluatePipeline(BasePipeline):
    """
    Atomic pipeline for evaluating models.
    
    Handles the complete evaluation workflow:
    - Load predictions and ground truth
    - Compute metrics
    - Save evaluation results
    """
    
    def __init__(
        self,
        config: Any,
        predictions: Optional[np.ndarray] = None,
        ground_truth: Optional[np.ndarray] = None,
        predictions_path: Optional[str] = None,
        ground_truth_path: Optional[str] = None,
        model_type: str = 'vision',  # 'vision' or 'tabular'
        **kwargs
    ):
        """
        Initialize evaluation pipeline.
        
        Args:
            config: Configuration object (VisionConfig or TabularConfig).
            predictions: Optional predictions array (if None, loads from predictions_path).
            ground_truth: Optional ground truth array (if None, loads from ground_truth_path).
            predictions_path: Optional path to predictions file.
            ground_truth_path: Optional path to ground truth file.
            model_type: Type of model ('vision' or 'tabular').
            **kwargs: Additional evaluation parameters.
        """
        super().__init__(config, **kwargs)
        self.predictions = predictions
        self.ground_truth = ground_truth
        self.predictions_path = Path(predictions_path) if predictions_path else None
        self.ground_truth_path = Path(ground_truth_path) if ground_truth_path else None
        self.model_type = model_type
        self.metrics = None
    
    def setup(self) -> None:
        """Setup evaluation pipeline."""
        logger.info("🔧 Setting up evaluation pipeline...")
        
        # Validate config
        validate_config_section_exists(self.config, 'paths')
        
        # Load predictions if not provided
        if self.predictions is None:
            if self.predictions_path is None:
                raise ValueError("Either predictions or predictions_path must be provided")
            if not self.predictions_path.exists():
                raise FileNotFoundError(f"Predictions file not found: {self.predictions_path}")
            self.predictions = np.load(self.predictions_path)
            logger.info(f"Loaded predictions from {self.predictions_path}")
        
        # Load ground truth if not provided
        if self.ground_truth is None:
            if self.ground_truth_path is None:
                raise ValueError("Either ground_truth or ground_truth_path must be provided")
            if not self.ground_truth_path.exists():
                raise FileNotFoundError(f"Ground truth file not found: {self.ground_truth_path}")
            self.ground_truth = np.load(self.ground_truth_path)
            logger.info(f"Loaded ground truth from {self.ground_truth_path}")
        
        # Validate shapes
        if self.predictions.shape != self.ground_truth.shape:
            raise ValueError(
                f"Shape mismatch: predictions {self.predictions.shape} vs "
                f"ground_truth {self.ground_truth.shape}"
            )
        
        # Create output directories
        if hasattr(self.config.paths, 'output_dir'):
            output_dir = Path(self.config.paths.output_dir)
            ensure_dir(output_dir)
            ensure_dir(output_dir / 'evaluation')
        
        logger.info("✅ Evaluation pipeline setup complete")
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute evaluation pipeline.
        
        Returns:
            Dictionary with evaluation results:
            - 'success': bool
            - 'metrics': dict (computed metrics)
            - 'output_path': str (path to saved metrics)
        """
        logger.info("📊 Computing evaluation metrics...")
        
        if self.model_type == 'vision':
            return self._evaluate_vision()
        elif self.model_type == 'tabular':
            return self._evaluate_tabular()
        else:
            raise ValueError(f"Unknown model type: {self.model_type}")
    
    def _save_metrics(self, output_path: Path) -> None:
        """Save metrics to JSON file."""
        ensure_dir(output_path.parent)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, indent=2)
        logger.info("✅ Evaluation complete")
        logger.info(f"  Metrics: {self.metrics}")
        logger.info(f"  Saved to {output_path}")

    def _evaluate_vision(self) -> Dict[str, Any]:
        """Evaluate vision model."""
        target_names = self.kwargs.get('target_names')
        self.metrics = calculate_regression_metrics(
            y_true=self.ground_truth,
            y_pred=self.predictions,
            target_names=target_names
        )
        output_path = Path(self.config.paths.output_dir) / 'evaluation' / 'metrics.json'
        self._save_metrics(output_path)
        return {
            'success': True,
            'metrics': self.metrics,
            'output_path': str(output_path)
        }

    def _evaluate_tabular(self) -> Dict[str, Any]:
        """Evaluate tabular model."""
        threshold = self.kwargs.get('threshold', 0.5)
        predictions_binary = (self.predictions >= threshold).astype(int)

        if self.ground_truth.ndim > 1 and self.ground_truth.shape[1] > 1:
            self.metrics = {
                'f1_macro': calculate_f1(self.ground_truth, predictions_binary, average='macro'),
                'f1_micro': calculate_f1(self.ground_truth, predictions_binary, average='micro'),
                'precision_macro': calculate_precision(self.ground_truth, predictions_binary, average='macro'),
                'recall_macro': calculate_recall(self.ground_truth, predictions_binary, average='macro'),
            }
            self.metrics['roc_auc_macro'] = calculate_roc_auc(
                self.ground_truth, self.predictions, average='macro'
            )
        else:
            self.metrics = {
                'f1': calculate_f1(self.ground_truth, predictions_binary, average='binary'),
                'precision': calculate_precision(self.ground_truth, predictions_binary, average='binary'),
                'recall': calculate_recall(self.ground_truth, predictions_binary, average='binary'),
            }

        output_path = Path(self.config.paths.output_dir) / 'evaluation' / 'metrics.json'
        self._save_metrics(output_path)
        return {
            'success': True,
            'metrics': self.metrics,
            'output_path': str(output_path)
        }
    
    def cleanup(self) -> None:
        """Cleanup evaluation resources."""
        # Nothing to clean up for evaluation
        pass
