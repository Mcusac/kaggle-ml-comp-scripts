"""Submission averaging workflow for combining multiple submission files."""

import time
import numpy as np
import shutil

from pathlib import Path
from typing import List, Optional, Dict, Any

from layers.layer_0_core.level_0 import ensure_dir, get_logger, validate_submission_format
from layers.layer_0_core.level_1 import BasePipeline
from layers.layer_0_core.level_2 import (
    simple_average,
    weighted_average,
    value_rank_average,
    value_percentile_average,
    power_average,
    geometric_mean,
    max_ensemble,
)

logger = get_logger(__name__)


class SubmissionAveragingWorkflow(BasePipeline):
    """
    Workflow for averaging multiple submission files.

    Combines multiple submission files using ensemble methods:
    average, weighted_average, max, geometric_mean, rank_average,
    power_average, percentile.
    """
    
    def __init__(
        self,
        config: Any,
        submission_files: List[str],
        ensemble_method: str = 'average',
        weights: Optional[List[float]] = None,
        output_path: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize submission averaging workflow.
        
        Args:
            config: Configuration object
            submission_files: List of paths to submission files
            ensemble_method: Ensemble method ('average', 'weighted_average', 'max',
                           'geometric_mean', 'rank_average', 'power_average', 'percentile')
            weights: Optional weights for weighted_average method
            output_path: Optional output path (default: auto-generated)
            **kwargs: Additional method-specific parameters:
                - power (float): Power for power_average method
                - percentile (float): Percentile for percentile method
        """
        super().__init__(config, **kwargs)
        self.submission_files = submission_files
        self.ensemble_method = ensemble_method
        self.weights = weights
        self.output_path = output_path
        self.valid_files = []
        self.final_path = None
    
    def setup(self) -> None:
        """Setup workflow: validate submission files."""
        logger.info("🔧 Setting up submission averaging workflow...")
        
        if not self.submission_files:
            raise ValueError("submission_files cannot be empty")
        
        # Validate submission files
        logger.info(f"Validating {len(self.submission_files)} submission files...")
        for i, filepath in enumerate(self.submission_files, 1):
            filepath = Path(filepath)
            logger.info(f"Validating [{i}/{len(self.submission_files)}]: {filepath.name}")
            
            is_valid, issues = validate_submission_format(filepath)
            
            if is_valid:
                logger.info("      ✓ Valid")
                self.valid_files.append(str(filepath))
            else:
                logger.error("      ❌ Invalid submission file:")
                for issue in issues:
                    logger.error(f"         - {issue}")
        
        if not self.valid_files:
            raise ValueError("No valid submission files found")
        
        if len(self.valid_files) < len(self.submission_files):
            logger.warning(f"Using {len(self.valid_files)}/{len(self.submission_files)} valid files")
        
        # Set output path if not provided
        if self.output_path is None:
            output_dir = Path(self.config.paths.output_dir) if hasattr(self.config, 'paths') else Path('.')
            output_dir = output_dir / 'ensembled'
            ensure_dir(output_dir)
            self.output_path = str(output_dir / f'submission_{self.ensemble_method}.tsv')
        
        logger.info("✅ Submission averaging workflow setup complete")
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute submission averaging workflow.
        
        Returns:
            Dictionary with results:
            - 'success': bool
            - 'output_path': str
            - 'method': str
            - 'num_files': int
        """
        logger.info("🚀 Starting submission averaging workflow...")
        start_time = time.time()
        
        if len(self.valid_files) == 1:
            logger.warning("Only one submission file provided, copying as-is")
            shutil.copy(self.valid_files[0], self.output_path)
            self.final_path = self.output_path
        else:
            # Load and ensemble submissions
            logger.info(f"Ensembling {len(self.valid_files)} submissions using method: {self.ensemble_method}")

            predictions_list = []
            for filepath in self.valid_files:
                logger.info(f"Loading: {Path(filepath).name}")
                preds = self._load_submission_file(filepath)
                predictions_list.append(preds)
            
            # Apply ensemble method
            ensembled = self._apply_ensemble_method(predictions_list)
            
            # Save ensembled submission
            self._save_submission(ensembled, self.output_path)
            self.final_path = self.output_path
        
        total_time = time.time() - start_time
        logger.info("✅ Submission averaging workflow complete!")
        logger.info(f"Total time: {total_time:.1f}s")
        logger.info(f"Final submission: {self.final_path}")
        
        return {
            'success': True,
            'output_path': self.final_path,
            'method': self.ensemble_method,
            'num_files': len(self.valid_files)
        }
    
    def _load_submission_file(self, filepath: str) -> Dict[tuple, float]:
        """
        Load submission file into dictionary format.
        
        Args:
            filepath: Path to submission file
            
        Returns:
            Dictionary mapping (protein_id, term) -> score
        """
        predictions = {}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                parts = line.split('\t')
                if len(parts) >= 3:
                    try:
                        protein_id = parts[0]
                        term = parts[1]
                        score = float(parts[2])
                        if 0 < score <= 1.0:
                            predictions[(protein_id, term)] = score
                    except (ValueError, IndexError):
                        continue
        
        return predictions
    
    def _convert_predictions_to_arrays(
        self,
        predictions_list: List[Dict[tuple, float]]
    ) -> tuple[List[np.ndarray], List[tuple]]:
        """Convert prediction dictionaries to aligned arrays."""
        # Get all unique keys
        all_keys = set()
        for preds in predictions_list:
            all_keys.update(preds.keys())
        
        # Create aligned prediction arrays
        key_list = sorted(all_keys)
        pred_arrays = []
        
        for preds in predictions_list:
            arr = np.array([preds.get(key, 0.0) for key in key_list])
            pred_arrays.append(arr)
        
        return pred_arrays, key_list
    
    def _apply_ensemble_to_arrays(
        self,
        pred_arrays: List[np.ndarray]
    ) -> np.ndarray:
        """Apply ensemble method to prediction arrays."""
        method_map = {
            'average': lambda: simple_average(pred_arrays, weights=self.weights),
            'weighted_average': lambda: self._apply_weighted_average(pred_arrays),
            'max': lambda: max_ensemble(pred_arrays, weights=self.weights),
            'geometric_mean': lambda: geometric_mean(pred_arrays, weights=self.weights),
            'rank_average': lambda: value_rank_average(pred_arrays, weights=self.weights),
            'power_average': lambda: self._apply_power_average(pred_arrays),
            'percentile': lambda: self._apply_percentile_average(pred_arrays)
        }
        
        if self.ensemble_method not in method_map:
            raise ValueError(f"Unknown ensemble method: {self.ensemble_method}")
        
        return method_map[self.ensemble_method]()
    
    def _apply_weighted_average(self, pred_arrays: List[np.ndarray]) -> np.ndarray:
        """Apply weighted average ensemble method."""
        if self.weights is None:
            raise ValueError("weights must be provided for weighted_average")
        return weighted_average(pred_arrays, self.weights)
    
    def _apply_power_average(self, pred_arrays: List[np.ndarray]) -> np.ndarray:
        """Apply power average ensemble method."""
        power = self.kwargs.get('power', 1.5)
        return power_average(pred_arrays, power=power, weights=self.weights)
    
    def _apply_percentile_average(self, pred_arrays: List[np.ndarray]) -> np.ndarray:
        """Apply percentile average ensemble method."""
        percentile = self.kwargs.get('percentile', 75.0)
        return value_percentile_average(pred_arrays, percentile=percentile, weights=self.weights)
    
    def _apply_ensemble_method(self, predictions_list: List[Dict[tuple, float]]) -> Dict[tuple, float]:
        """
        Apply ensemble method to list of prediction dictionaries.
        
        Args:
            predictions_list: List of prediction dicts mapping (protein_id, term) -> score
            
        Returns:
            Ensembled predictions dictionary
        """
        # Convert to arrays
        pred_arrays, key_list = self._convert_predictions_to_arrays(predictions_list)
        
        # Apply ensemble method
        ensembled_arr = self._apply_ensemble_to_arrays(pred_arrays)
        
        # Convert back to dictionary
        ensembled = {
            key: float(score)
            for key, score in zip(key_list, ensembled_arr)
            if score > 0  # Only keep non-zero predictions
        }
        
        return ensembled
    
    def _save_submission(self, predictions: Dict[tuple, float], output_path: str) -> None:
        """
        Save ensembled predictions to submission file.
        
        Args:
            predictions: Dictionary mapping (protein_id, term) -> score
            output_path: Path to save submission file
        """
        output_path = Path(output_path)
        ensure_dir(output_path.parent)

        # Sort by (protein_id, term) for consistent output
        sorted_keys = sorted(predictions.keys())
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for protein_id, term in sorted_keys:
                score = predictions[(protein_id, term)]
                f.write(f"{protein_id}\t{term}\t{score:.6f}\n")
        
        logger.info(f"✓ Saved ensembled submission: {output_path}")
        logger.info(f"  Total predictions: {len(predictions):,}")
    
    def cleanup(self) -> None:
        """Cleanup workflow resources."""
        # Nothing specific to clean up
        pass
