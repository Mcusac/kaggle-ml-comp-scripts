"""Grid search context builder for CSIRO CLI handlers."""

from typing import Any

from layers.layer_0_core.level_1 import get_regression_grid
from layers.layer_0_core.level_2 import find_feature_cache, load_features

from layers.layer_1_competition.level_0_infra.level_1 import build_grid_search_context

from layers.layer_1_competition.level_1_impl.level_csiro.level_0 import calc_metric
from layers.layer_1_competition.level_1_impl.level_csiro.level_1 import test_pipeline
from layers.layer_1_competition.level_1_impl.level_csiro.level_2 import (
    initialize_working_metadata_files,
    load_regression_gridsearch_results,
)

from layers.layer_1_competition.level_1_impl.level_csiro.level_3 import (
    get_or_create_regression_variant_id,
    save_regression_gridsearch_result,
)


def _make_metadata_handler() -> Any:
    """Build CSIRO metadata handler for grid search context."""
    class _Meta:
        @staticmethod
        def get_or_create_variant_id(regression_model_type, hyperparameters):
            return get_or_create_regression_variant_id(
                regression_model_type=regression_model_type,
                hyperparameters=hyperparameters,
            )

        @staticmethod
        def save_gridsearch_result(
            regression_model_type, variant_id, feature_filename, cv_score, fold_scores, hyperparameters
        ):
            return save_regression_gridsearch_result(
                regression_model_type=regression_model_type,
                variant_id=variant_id,
                feature_filename=feature_filename,
                cv_score=cv_score,
                fold_scores=fold_scores,
                hyperparameters=hyperparameters,
            )

        @staticmethod
        def initialize_metadata_files(regression_model_type):
            return initialize_working_metadata_files(regression_model_type)

    return _Meta()


def _make_feature_cache_loader() -> Any:
    """Build CSIRO feature cache loader for grid search context."""
    class _Loader:
        @staticmethod
        def find_feature_cache(filename):
            return find_feature_cache(filename)

        @staticmethod
        def load_features(path):
            return load_features(path)

    return _Loader()


def get_grid_search_context() -> Any:
    """Build grid search context for CSIRO orchestration."""
    return build_grid_search_context(
        "csiro",
        metric_calculator=calc_metric,
        test_pipeline=test_pipeline,
        load_regression_gridsearch_results=load_regression_gridsearch_results,
        metadata_handler=_make_metadata_handler(),
        parameter_grid_fn=get_regression_grid,
        feature_cache_loader=_make_feature_cache_loader(),
    )
