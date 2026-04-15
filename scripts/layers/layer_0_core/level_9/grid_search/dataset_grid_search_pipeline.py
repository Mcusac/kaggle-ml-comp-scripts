"""Dataset grid search pipeline. Requires contest_context from contest layer (orchestration does not import contest)."""

from typing import Any, Dict, Optional, Union

from layers.layer_0_core.level_0 import (
    AVAILABLE_AUGMENTATION,
    AVAILABLE_PREPROCESSING,
    BEST_VARIANT_FILE_DATASET,
    get_logger,
)
from layers.layer_0_core.level_4 import save_json
from layers.layer_0_core.level_8 import DatasetGridSearch

logger = get_logger(__name__)


class SimplePaths:
    """Thin wrapper over contest paths so execution can access output_dir, model_dir, data_root without contest import."""

    def __init__(self, paths_obj: Any) -> None:
        self._raw = paths_obj
        self.output_dir = paths_obj.get_output_dir()
        self.model_dir = paths_obj.get_models_base_dir()

    def get_output_dir(self) -> str:
        return self.output_dir

    def get_models_base_dir(self) -> str:
        return self.model_dir

    def get_data_root(self) -> Optional[str]:
        fn = getattr(self._raw, 'get_data_root', None)
        if callable(fn):
            return fn()
        return getattr(self._raw, 'local_data_root', None)


def attach_paths_to_config(config: Any, paths: Any) -> None:
    """Attach a simple paths wrapper to config if missing (so execution can get data_root without contest import)."""
    if hasattr(config, 'paths'):
        return
    config.paths = SimplePaths(paths)


def dataset_grid_search_pipeline(
    contest_context: Any,
    train_pipeline_fn: Optional[Any] = None,
    config: Optional[Union[Any, Dict[str, Any]]] = None,
    **kwargs,
) -> None:
    """
    Run dataset grid search. Contest layer passes contest_context (get_paths, get_config).
    """
    paths = contest_context.get_paths()
    if config is None:
        config = contest_context.get_config()
    attach_paths_to_config(config, paths)

    # Create grid search instance (train_pipeline_fn provided by contest)
    grid_search = DatasetGridSearch(
        config=config,
        grid_search_type='dataset',
        results_filename='gridsearch_results.json',
        quick_mode=kwargs.get('quick_mode', False),
        train_pipeline_fn=train_pipeline_fn,
    )

    # Setup
    grid_search.setup()

    # Generate variant grid
    variant_grid = grid_search._generate_variant_grid()
    total_variants = len(variant_grid)
    logger.info(f"Total dataset variants to test: {total_variants}")

    # Execute grid search
    result = grid_search.execute()

    # Save best variant summary
    best_variant_file = grid_search.grid_search_dir / BEST_VARIANT_FILE_DATASET
    save_json(
        {
            'best_score': result.get('best_score', -float('inf')),
            'best_variant': result.get('best_variant'),
            'total_variants': total_variants,
            'completed_variants': result.get('completed_variants', 0),
            'failed_variants': result.get('failed_variants', 0)
        },
        best_variant_file
    )

    logger.info("=" * 60)
    logger.info("Dataset grid search complete!")
    logger.info(f"Best score: {result.get('best_score', -float('inf')):.4f}")
    logger.info(f"Results saved to: {grid_search.results_file}")
    logger.info(f"Best variant saved to: {best_variant_file}")
    logger.info("=" * 60)

    # Cleanup
    grid_search.cleanup()


def test_max_augmentation_pipeline(
    contest_context: Any,
    preprocessing_list: Optional[list] = None,
    augmentation_list: Optional[list] = None,
    config: Optional[Union[Any, Dict[str, Any]]] = None,
    **kwargs,
) -> None:
    """
    Test the maximally augmented dataset variant. Contest passes contest_context; lists from components if omitted.
    Requires train_pipeline_fn in kwargs (e.g. train_pipeline_fn=contest.get_train_pipeline_fn()).
    """
    paths = contest_context.get_paths()
    if config is None:
        config = contest_context.get_config()
    attach_paths_to_config(config, paths)

    if preprocessing_list is None or augmentation_list is None:
        all_prep = sorted(AVAILABLE_PREPROCESSING)
        preprocessing_list = [p for p in all_prep if p not in ['resize', 'normalize']]
        augmentation_list = sorted(AVAILABLE_AUGMENTATION)
    variant = (preprocessing_list, augmentation_list)

    logger.info("=" * 60)
    logger.info("Max Augmentation Quick Test Mode")
    logger.info("=" * 60)
    logger.info(f"Preprocessing: {preprocessing_list}")
    logger.info(f"Augmentation: {augmentation_list}")
    logger.info("=" * 60)

    grid_search = DatasetGridSearch(
        config=config,
        grid_search_type='dataset',
        results_filename='gridsearch_results.json',
        train_pipeline_fn=kwargs.get('train_pipeline_fn'),
    )

    # Setup
    grid_search.setup()

    # Run variant (single-variant test)
    result = grid_search._run_variant(variant, 0, total_variants=1)

    logger.info("=" * 60)
    logger.info("Max Augmentation Quick Test Complete!")
    logger.info("=" * 60)
