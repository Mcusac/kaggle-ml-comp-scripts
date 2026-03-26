"""End-to-end hyperparameter grid search implementation."""

from typing import Any, Dict, Optional, Tuple, Union

from level_0 import (
    BEST_HYPERPARAMETERS_FILE,
    ConfigValidationError,
    RESULTS_FILE_GRIDSEARCH,
    SEARCH_TYPE_THOROUGH,
    get_logger,
)
from level_1 import get_transformer_hyperparameter_grid
from level_4 import save_json
from level_7 import HyperparameterGridSearchBase
from level_8 import create_end_to_end_variant_result, extract_variant_config
from level_9 import attach_paths_to_config

logger = get_logger(__name__)


class EndToEndGridSearch(HyperparameterGridSearchBase):
    """
    End-to-end hyperparameter grid search.

    Tests hyperparameter combinations with full training pipeline.
    """

    def __init__(
        self,
        config: Union[Any, Dict[str, Any]],
        search_type: str = SEARCH_TYPE_THOROUGH,
        train_pipeline_fn: Optional[Any] = None,
        **kwargs,
    ):
        """
        Initialize hyperparameter grid search.

        Args:
            config: Configuration object or dict.
            search_type: Search type ('defaults', 'quick', 'in_depth', 'thorough', etc.).
            train_pipeline_fn: Contest-provided train_pipeline (orchestration must not import contest).
            **kwargs: Additional arguments.
        """
        super().__init__(
            config=config,
            grid_search_type="hyperparameter",
            results_filename=RESULTS_FILE_GRIDSEARCH,
            quick_mode=(search_type == "quick"),
            **kwargs,
        )
        self.search_type = search_type
        self.train_pipeline_fn = train_pipeline_fn

    def _create_variant_key(self, variant: tuple) -> Tuple:
        """Create variant key from hyperparameter combination."""
        return self._create_variant_key_from_hyperparameters(variant)

    def _create_variant_key_from_result(self, result: Dict[str, Any]) -> Optional[Tuple]:
        """Create variant key from result dictionary."""
        hyperparameters = result.get("hyperparameters", {})
        if not hyperparameters:
            return None
        return tuple(sorted(hyperparameters.items()))

    def _run_variant(self, variant: tuple, variant_index: int, **kwargs) -> Dict[str, Any]:
        """Run a single hyperparameter variant."""
        variant_config_copy, model, n_folds, batch_size_used, variant_id, data_root = extract_variant_config(
            self.config, self.param_names, variant, variant_index
        )
        hyperparameters = dict(zip(self.param_names, variant))

        try:
            if self.train_pipeline_fn is None:
                raise ConfigValidationError(
                    "train_pipeline_fn is required. Contest layer must pass its train_pipeline when calling hyperparameter grid search."
                )
            cv_score, fold_scores = self.train_pipeline_fn(
                data_root=data_root,
                model=model,
                n_folds=n_folds,
                **(
                    {}
                    if not isinstance(variant_config_copy, dict)
                    else {
                        k: v
                        for k, v in variant_config_copy.items()
                        if k not in ["data_root", "model", "model_name", "n_folds", "model_dir"]
                    }
                ),
            )

            result = create_end_to_end_variant_result(
                variant_index,
                variant_id,
                cv_score,
                fold_scores,
                hyperparameters,
                self.config,
                batch_size_used,
            )

            return result

        except Exception as e:
            logger.error(f"Error training variant {variant_id}: {e}", exc_info=True)

            result = create_end_to_end_variant_result(
                variant_index,
                variant_id,
                None,
                None,
                hyperparameters,
                self.config,
                batch_size_used,
                error=str(e),
            )

            return result


def hyperparameter_grid_search_pipeline(
    contest_context: Any,
    train_pipeline_fn: Optional[Any] = None,
    config: Optional[Union[Any, Dict[str, Any]]] = None,
    search_type: str = SEARCH_TYPE_THOROUGH,
    **kwargs,
) -> None:
    """
    Run hyperparameter grid search. Contest layer passes contest_context and train_pipeline_fn.

    Args:
        contest_context: Must provide get_paths() and get_config().
        train_pipeline_fn: Callable (data_root, model, n_folds, **config_overrides) -> (cv_score, fold_scores).
        config: Optional; defaults to contest_context.get_config().
        search_type: 'defaults', 'quick', 'in_depth', 'thorough', etc.
        **kwargs: Passed to EndToEndGridSearch.
    """
    paths = contest_context.get_paths()
    if config is None:
        config = contest_context.get_config()
    attach_paths_to_config(config, paths)

    grid_search = EndToEndGridSearch(
        config=config,
        search_type=search_type,
        train_pipeline_fn=train_pipeline_fn,
        **kwargs,
    )

    grid_search.setup()

    param_grid = get_transformer_hyperparameter_grid(search_type)
    grid_search.setup_parameter_grid(param_grid)

    variant_grid = grid_search._generate_variant_grid()
    total_variants = len(variant_grid)
    logger.info(f"Total hyperparameter variants to test: {total_variants}")

    result = grid_search.execute()

    best_hyperparameters_file = grid_search.grid_search_dir / BEST_HYPERPARAMETERS_FILE
    save_json(
        {
            "best_score": result.get("best_score", -float("inf")),
            "best_variant": result.get("best_variant"),
            "total_variants": total_variants,
            "completed_variants": result.get("completed_variants", 0),
            "failed_variants": result.get("failed_variants", 0),
        },
        best_hyperparameters_file,
    )

    logger.info("=" * 60)
    logger.info("Hyperparameter grid search complete!")
    logger.info(f"Best score: {result.get('best_score', -float('inf')):.4f}")
    logger.info(f"Results saved to: {grid_search.results_file}")
    logger.info(f"Best hyperparameters saved to: {best_hyperparameters_file}")
    logger.info("=" * 60)

    grid_search.cleanup()
