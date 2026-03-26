"""DatasetGridSearch extends framework GridSearchBase; config must have paths set by caller (contest_context)."""

from typing import Dict, List, Any, Optional, Tuple

from level_0 import (
    get_logger,
    GRID_SEARCH_TYPE_DATASET,
    RESULTS_FILE_GRIDSEARCH
)
from level_1 import generate_variant_grid
from level_6 import GridSearchBase, create_variant_key, create_variant_key_from_result, get_default_hyperparameters
from level_7 import run_single_variant


logger = get_logger(__name__)


class DatasetGridSearch(GridSearchBase):
    """
    Dataset grid search implementation.

    Tests all combinations of optional preprocessing and augmentation methods.
    Requires train_pipeline_fn from contest layer (orchestration must not import contest).
    """

    def __init__(self, train_pipeline_fn: Optional[Any] = None, **kwargs):
        self.train_pipeline_fn = train_pipeline_fn
        kwargs.pop('train_pipeline_fn', None)
        super().__init__(**kwargs)

    def _get_grid_search_type(self) -> str:
        """Return grid search type identifier."""
        return GRID_SEARCH_TYPE_DATASET

    def _get_results_filename(self) -> str:
        """Return results filename."""
        return RESULTS_FILE_GRIDSEARCH

    def _generate_variant_grid(self) -> List[Tuple[List[str], List[str]]]:
        """Generate the grid of preprocessing/augmentation variants."""
        return generate_variant_grid()

    def _create_variant_key(self, variant: Tuple[List[str], List[str]]) -> Tuple:
        """
        Create variant key from preprocessing/augmentation variant.

        Args:
            variant: Tuple of (preprocessing_list, augmentation_list).

        Returns:
            Variant key tuple.
        """
        preprocessing_list, augmentation_list = variant
        default_hyperparameters = get_default_hyperparameters()
        return create_variant_key(
            config=self.config,
            preprocessing_list=preprocessing_list,
            augmentation_list=augmentation_list,
            hyperparameters=default_hyperparameters
        )

    def _create_variant_key_from_result(self, result: Dict[str, Any]) -> Optional[Tuple]:
        """
        Create variant key from result dictionary.

        Args:
            result: Result dictionary from JSON file.

        Returns:
            Variant key tuple or None if result is invalid.
        """
        return create_variant_key_from_result(result, config=self.config)

    def _run_variant(
        self,
        variant: Tuple[List[str], List[str]],
        variant_index: int,
        total_variants: Optional[int] = None,
        actual_variant_num: Optional[int] = None,
        total_to_test: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Run a single dataset variant.

        Args:
            variant: Tuple of (preprocessing_list, augmentation_list).
            variant_index: Index of variant in grid.
            total_variants: Total number of variants.
            actual_variant_num: Optional actual variant number being tested.
            total_to_test: Optional total number of variants actually being tested.

        Returns:
            Dictionary with variant results.
        """
        preprocessing_list, augmentation_list = variant
        if total_variants is None:
            total_variants = len(self._generate_variant_grid())

        # Run the variant using execution function (train_pipeline_fn provided by contest)
        cv_score, fold_scores, result, variant_model_dir = run_single_variant(
            variant=(preprocessing_list, augmentation_list),
            variant_index=variant_index,
            total_variants=total_variants,
            config=self.config,
            train_csv_path=self.get_train_csv_path(),
            base_model_dir=self.base_model_dir,
            device=self.device,
            results_file=self.results_file,
            train_pipeline_fn=self.train_pipeline_fn,
        )

        return result
