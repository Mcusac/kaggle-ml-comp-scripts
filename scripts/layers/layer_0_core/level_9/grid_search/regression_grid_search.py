"""Regression head hyperparameter grid search pipeline."""

import numpy as np

from typing import Optional, Union, Dict, Any, Tuple, List

from level_0 import get_logger, create_error_result_dict
from level_6 import create_variant_specific_data, create_regression_variant_key_from_result
from level_7 import HyperparameterGridSearchBase
from level_8 import run_regression_cv_fold, create_regression_variant_result

logger = get_logger(__name__)


class RegressionGridSearch(HyperparameterGridSearchBase):
    """
    Regression head hyperparameter grid search.

    Tests hyperparameter combinations for regression models with pre-extracted features.
    """

    def __init__(
        self,
        config: Union[Any, Dict[str, Any]],
        regression_model_type: str,
        metadata_handler: Optional[Any] = None,
        metric_calculator: Optional[Any] = None,
        **kwargs
    ):
        """
        Initialize regression grid search.

        Args:
            config: Configuration object or dict.
            regression_model_type: Type of regression model ('lgbm', 'xgboost', 'ridge').
            metadata_handler: From contest_context.get_metadata_handler(); required for variant persistence.
            metric_calculator: From contest_context.get_metric_calculator(); required for fold scoring.
            **kwargs: Additional arguments.
        """
        super().__init__(
            config=config,
            grid_search_type='regression',
            results_filename='gridsearch_results.json',
            **kwargs
        )
        self.regression_model_type = regression_model_type
        self._metadata_handler = metadata_handler
        self._metric_calculator = metric_calculator
        self.all_features = None
        self.all_targets = None
        self.fold_assignments = None
        self.feature_filename = None

    def setup_features(
        self,
        all_features: Any,
        all_targets: Any,
        fold_assignments: Any,
        feature_filename: str,
        param_names: List[str],
        param_grid: Dict[str, List[Any]]
    ) -> None:
        """
        Setup feature data for regression grid search.

        Args:
            all_features: All features array.
            all_targets: All targets array.
            fold_assignments: Fold assignments array.
            feature_filename: Feature filename.
            param_names: Parameter names list.
            param_grid: Parameter grid dictionary.
        """
        self.all_features = all_features
        self.all_targets = all_targets
        self.fold_assignments = fold_assignments
        self.feature_filename = feature_filename
        self.param_names = param_names
        self.param_grid = param_grid

    def _get_grid_search_type(self) -> str:
        return 'regression'

    def _get_results_filename(self) -> str:
        return 'gridsearch_results.json'

    def _create_variant_key(self, variant: tuple) -> Tuple:
        """Create variant key from hyperparameter combination."""
        return (self.feature_filename, self._create_variant_key_from_hyperparameters(variant))

    def _create_variant_key_from_result(self, result: Dict[str, Any]) -> Optional[Tuple]:
        """Create variant key from result dictionary."""
        return create_regression_variant_key_from_result(result)

    def _run_variant(self, variant: tuple, variant_index: int, **kwargs) -> Dict[str, Any]:
        """Run a single regression hyperparameter variant."""

        # Create hyperparameters dict
        hyperparameters = dict(zip(self.param_names, variant))

        if self._metadata_handler is None:
            raise ValueError("metadata_handler is required; pass contest_context.get_metadata_handler()")
        variant_id, metadata_variant_index = self._metadata_handler.get_or_create_variant_id(
            self.regression_model_type,
            hyperparameters=hyperparameters,
        )

        # Validate that features are loaded
        if self.all_features is None or self.all_targets is None or self.fold_assignments is None:
            raise ValueError(
                "Features must be loaded before running regression variants. "
                "Call setup_features() first."
            )

        # Get number of folds
        n_folds = 5
        if isinstance(self.config, dict):
            n_folds = self.config.get('n_folds', 5)
        elif hasattr(self.config, 'cv'):
            n_folds = getattr(self.config.cv, 'n_folds', 5)

        try:

            if self._metric_calculator is None:
                raise ValueError("metric_calculator is required; pass contest_context.get_metric_calculator()")
            fold_scores = []
            for fold in range(n_folds):
                fold_score = run_regression_cv_fold(
                    fold, n_folds, self.all_features, self.all_targets, self.fold_assignments,
                    self.regression_model_type, hyperparameters, self.config,
                    metric_calculator=self._metric_calculator,
                )
                fold_scores.append(fold_score)

            # Calculate average CV score
            cv_score = np.mean(fold_scores)
            logger.info("=" * 60)
            logger.info(f"Average CV Score: {cv_score:.4f}")
            logger.info(f"Fold scores: {[f'{s:.4f}' for s in fold_scores]}")
            logger.info("=" * 60)

            # Create result
            result = create_regression_variant_result(
                metadata_variant_index, variant_id, cv_score, fold_scores, hyperparameters,
                self.config, self.feature_filename, self.regression_model_type
            )

            # Framework GridSearchBase tracks best_score via the `score` key.
            result["score"] = float(cv_score)
            result["cv_score"] = float(cv_score)
            result["metadata_variant_index"] = int(metadata_variant_index)

            self._metadata_handler.save_gridsearch_result(
                self.regression_model_type,
                variant_id=variant_id,
                feature_filename=self.feature_filename,
                cv_score=float(cv_score),
                fold_scores=[float(s) for s in fold_scores],
                hyperparameters=hyperparameters,
            )

            return result

        except Exception as e:
            logger.error(f"Error training variant {variant_id}: {e}", exc_info=True)

            # Create error result
            variant_specific_data = create_variant_specific_data(
                config=self.config,
                hyperparameters=hyperparameters,
                feature_filename=self.feature_filename
            )
            result = create_error_result_dict(
                variant_index=variant_index,
                variant_id=variant_id,
                error=str(e),
                batch_size_used=None,
                batch_size_reduced=False,
                variant_specific_data=variant_specific_data
            )

            result['regression_model_type'] = self.regression_model_type
            result['feature_filename'] = self.feature_filename
            result['metadata_variant_index'] = int(metadata_variant_index) if 'metadata_variant_index' in locals() else None

            return result


def regression_grid_search_pipeline(
    contest_context: Any,
    config: Optional[Union[Any, Dict[str, Any]]] = None,
    feature_filename: Optional[str] = None,
    regression_model_type: Optional[str] = None,
    search_type: str = 'quick',
    **kwargs
) -> None:
    """
    Run regression grid search using pre-extracted features.
    Requires contest_context from contest layer (paths, config, metadata, feature cache, parameter grid).

    Args:
        contest_context: From contest CLI; provides get_paths, get_config, get_metadata_handler, get_feature_cache_loader, get_parameter_grid_fn.
        config: Configuration object or dict (default: from contest_context).
        feature_filename: Feature filename (e.g., "variant_0100_features.npz").
        regression_model_type: Type of regression model ('lgbm', 'xgboost', 'ridge').
        search_type: Search type ('defaults', 'quick', 'in_depth', 'thorough').
        **kwargs: Additional arguments.
    """
    paths = contest_context.get_paths()
    if config is None:
        config = contest_context.get_config()

    if not feature_filename:
        raise ValueError("feature_filename is required for regression grid search")
    if not regression_model_type:
        raise ValueError("regression_model_type is required for regression grid search")

    metadata_handler = contest_context.get_metadata_handler()
    metadata_handler.initialize_metadata_files(regression_model_type)

    metric_calculator = contest_context.get_metric_calculator()
    grid_search = RegressionGridSearch(
        config=config,
        regression_model_type=regression_model_type,
        metadata_handler=metadata_handler,
        metric_calculator=metric_calculator,
        **kwargs
    )

    grid_search.setup()

    loader = contest_context.get_feature_cache_loader()
    cache_path = loader.find_feature_cache(feature_filename)
    if cache_path is None:
        raise FileNotFoundError(
            f"Feature cache not found for filename: {feature_filename}. "
            f"Please extract features first."
        )

    logger.info(f"Loading features from cache: {cache_path}")
    all_features, all_targets, fold_assignments, cache_metadata = loader.load_features(cache_path)
    logger.info(f"Loaded features: {all_features.shape}, targets: {all_targets.shape}")

    get_param_grid = contest_context.get_parameter_grid_fn()
    param_grid = get_param_grid(
        model_type=regression_model_type,
        search_type=search_type,
    )
    grid_search.setup_parameter_grid(param_grid)

    # Setup features
    grid_search.setup_features(
        all_features=all_features,
        all_targets=all_targets,
        fold_assignments=fold_assignments,
        feature_filename=feature_filename,
        param_names=list(param_grid.keys()),
        param_grid=param_grid
    )

    # Generate variant grid
    variant_grid = grid_search._generate_variant_grid()
    total_variants = len(variant_grid)
    logger.info(f"Total regression hyperparameter variants to test: {total_variants}")

    # Execute grid search
    result = grid_search.execute()

    logger.info("=" * 60)
    logger.info("Regression grid search complete!")
    logger.info(f"Best score: {result.get('best_score', -float('inf')):.4f}")
    logger.info(f"Results saved to: {grid_search.results_file}")
    logger.info("=" * 60)

    # Cleanup
    grid_search.cleanup()
