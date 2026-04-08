"""Grid-search context types (data-only, no registry access)."""

from typing import Any, Callable, Optional


class ContestGridSearchContext:
    """Context object providing contest paths, config, and injected overrides."""

    def __init__(
        self,
        *,
        paths: Any,
        config: Any,
        data_schema: Any,
        post_processor: Any,
        metric_calculator: Optional[Callable],
        test_pipeline: Optional[Callable],
        load_regression_gridsearch_results: Optional[Callable],
        metadata_handler: Optional[Any],
        parameter_grid_fn: Optional[Callable],
        feature_cache_loader: Optional[Any],
    ) -> None:
        self._paths = paths
        self._config = config
        self._data_schema = data_schema
        self._post_processor = post_processor
        self._metric_calculator = metric_calculator
        self._test_pipeline = test_pipeline
        self._load_regression_gridsearch_results = load_regression_gridsearch_results
        self._metadata_handler = metadata_handler
        self._parameter_grid_fn = parameter_grid_fn
        self._feature_cache_loader = feature_cache_loader

    def get_paths(self):
        return self._paths

    def get_config(self):
        return self._config

    def get_metric_calculator(self):
        return self._metric_calculator

    def get_data_schema(self):
        return self._data_schema

    def get_post_processor(self):
        return self._post_processor

    def get_test_pipeline(self):
        return self._test_pipeline

    def load_regression_gridsearch_results(
        self, regression_model_type, variant_id=None, feature_filename=None
    ):
        if self._load_regression_gridsearch_results is None:
            raise NotImplementedError("load_regression_gridsearch_results not provided")
        return self._load_regression_gridsearch_results(
            regression_model_type=regression_model_type,
            variant_id=variant_id,
            feature_filename=feature_filename,
        )

    def get_metadata_handler(self):
        return self._metadata_handler

    def get_feature_cache_loader(self):
        return self._feature_cache_loader

    def get_parameter_grid_fn(self):
        return self._parameter_grid_fn

