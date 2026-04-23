"""Hyperparameter grid search."""

import copy
from itertools import product
from typing import Any, Dict, List, Tuple

from layers.layer_0_core.level_0 import ensure_dir, get_logger
from layers.layer_0_core.level_4 import EvaluatePipeline
from layers.layer_0_core.level_6 import GridSearchBase, PredictPipeline
from layers.layer_0_core.level_8 import TrainPipeline

_logger = get_logger(__name__)


class HyperparameterGridSearch(GridSearchBase):
    """
    Grid search for hyperparameter optimization.

    Tests different combinations of hyperparameters and finds the best configuration.
    """

    def __init__(
        self,
        config: Any,
        param_grid: Dict[str, List[Any]],
        model_type: str = 'vision',
        **kwargs
    ):
        """
        Initialize hyperparameter grid search.

        Args:
            config: Configuration object.
            param_grid: Dictionary mapping parameter names to value lists.
                       Example: {'learning_rate': [1e-3, 1e-4], 'batch_size': [16, 32]}
            model_type: Type of model ('vision' or 'tabular').
            **kwargs: Additional parameters passed to training pipeline.
        """
        super().__init__(
            config=config,
            grid_search_type='hyperparameter',
            results_filename='hyperparameter_results.json',
            **kwargs
        )
        self.param_grid = param_grid
        self.param_names = list(param_grid.keys())
        self.all_combinations: List[Tuple] = []
        self.model_type = model_type

    def setup(self) -> None:
        """Setup hyperparameter grid search."""
        super().setup()

        # Generate all combinations
        param_values = list(self.param_grid.values())
        self.all_combinations = list(product(*param_values))

        _logger.info(f"  Parameter grid: {self.param_names}")
        _logger.info(f"  Total combinations: {len(self.all_combinations):,}")

    def _generate_variant_grid(self) -> List[Tuple]:
        """Generate the grid of hyperparameter combinations."""
        return self.all_combinations

    def _create_variant_key(self, variant: Tuple) -> Tuple:
        """Create unique key for variant tracking."""
        # Create dict and sort for consistent key
        hyperparameters = dict(zip(self.param_names, variant))
        return tuple(sorted(hyperparameters.items()))

    def _run_variant(self, variant: Tuple, variant_index: int) -> Dict[str, Any]:
        """
        Execute a single hyperparameter variant.

        Args:
            variant: Tuple of hyperparameter values.
            variant_index: Index of variant in grid.

        Returns:
            Dictionary with variant results.
        """
        # Create hyperparameter dict
        hyperparameters = dict(zip(self.param_names, variant))

        _logger.info(f"Testing hyperparameters: {hyperparameters}")

        # Apply hyperparameters to config
        modified_config = self._apply_hyperparameters(hyperparameters)

        # Create variant-specific output directory
        variant_dir = self.grid_search_dir / f"variant_{variant_index}"
        ensure_dir(variant_dir)

        # Update config paths for this variant
        modified_config.paths.output_dir = str(variant_dir)

        try:
            # Train model
            train_pipeline = TrainPipeline(
                config=modified_config,
                model_type=self.model_type,
                checkpoint_dir=str(variant_dir / 'checkpoints'),
                **self.kwargs
            )

            train_results = train_pipeline.run()

            if not train_results['success']:
                raise RuntimeError("Training failed")

            # Get score (primary metric)
            score = train_results['metrics'].get('best_score', -float('inf'))

            # Evaluate if validation data available
            metrics = train_results['metrics'].copy()

            if 'val_data' in self.kwargs or 'X_val' in self.kwargs:
                predict_pipeline = PredictPipeline(
                    config=modified_config,
                    model_path=train_results['model_path'],
                    model_type=self.model_type,
                    **{k: v for k, v in self.kwargs.items() if k.startswith(('test_', 'X_', 'val_'))}
                )

                predict_results = predict_pipeline.run()

                # Evaluate predictions
                if 'y_val' in self.kwargs or 'val_targets' in self.kwargs:
                    evaluate_pipeline = EvaluatePipeline(
                        config=modified_config,
                        predictions=predict_results['predictions'],
                        ground_truth=self.kwargs.get('y_val') or self.kwargs.get('val_targets'),
                        model_type=self.model_type
                    )

                    eval_results = evaluate_pipeline.run()
                    metrics.update(eval_results['metrics'])
                    score = eval_results['metrics'].get('f1_macro', score)

            return {
                'success': True,
                'score': score,
                'metrics': metrics,
                'variant': hyperparameters,
                'model_path': train_results['model_path'],
                'variant_index': variant_index
            }

        except Exception as e:
            _logger.error(f"Variant failed: {str(e)}")
            return {
                'success': False,
                'score': -float('inf'),
                'error': str(e),
                'variant': hyperparameters,
                'variant_index': variant_index
            }

    def _apply_hyperparameters(self, hyperparameters: Dict[str, Any]) -> Any:
        """
        Apply hyperparameters to config.

        Creates a modified copy of the config with hyperparameters applied.

        Args:
            hyperparameters: Dictionary of hyperparameter values.

        Returns:
            Modified config object.
        """
        modified_config = copy.deepcopy(self.config)

        # Apply hyperparameters to training config
        for key, value in hyperparameters.items():
            if hasattr(modified_config, 'training'):
                if hasattr(modified_config.training, key):
                    setattr(modified_config.training, key, value)
                elif key == 'batch_size':
                    if hasattr(modified_config.training, 'batch_size'):
                        modified_config.training.batch_size = value
                elif key == 'learning_rate':
                    if hasattr(modified_config.training, 'learning_rate'):
                        modified_config.training.learning_rate = value
            elif hasattr(modified_config, key):
                setattr(modified_config, key, value)

        return modified_config
