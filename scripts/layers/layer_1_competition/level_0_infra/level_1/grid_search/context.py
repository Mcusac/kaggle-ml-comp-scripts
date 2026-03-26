"""Generic grid search context builder for contest pipelines."""

from typing import Any, Callable, Optional

from layers.layer_1_competition.level_0_infra.level_1.registry import get_contest


class _ContestGridSearchContext:
    """Context object providing contest paths, config, and injected overrides."""

    def __init__(
        self,
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
    ):
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
            raise NotImplementedError(
                "load_regression_gridsearch_results not provided"
            )
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


def build_grid_search_context(
    contest_name: str,
    *,
    metric_calculator: Optional[Callable] = None,
    test_pipeline: Optional[Callable] = None,
    load_regression_gridsearch_results: Optional[Callable] = None,
    metadata_handler: Optional[Any] = None,
    parameter_grid_fn: Optional[Callable] = None,
    feature_cache_loader: Optional[Any] = None,
) -> Any:
    """
    Build grid search context for orchestration.

    Base context (paths, config, data_schema, post_processor) comes from
    contest registry. Contest-specific behavior is injected via overrides.

    Args:
        contest_name: Registered contest name (e.g., 'csiro').
        metric_calculator: Optional (y_pred, y_true, config?) -> score.
        test_pipeline: Optional inference pipeline.
        load_regression_gridsearch_results: Optional loader for grid search results.
        metadata_handler: Optional object with get_or_create_variant_id, save_gridsearch_result, initialize_metadata_files.
        parameter_grid_fn: Optional function returning parameter grid.
        feature_cache_loader: Optional object with find_feature_cache, load_features.

    Returns:
        Context object with get_paths, get_config, get_metric_calculator, get_data_schema,
        get_post_processor, get_test_pipeline, load_regression_gridsearch_results,
        get_metadata_handler, get_feature_cache_loader, get_parameter_grid_fn.
    """
    contest = get_contest(contest_name)
    paths = contest["paths"]()
    config = contest["config"]()
    data_schema = contest.get("data_schema")
    data_schema = data_schema() if data_schema else None
    post_processor = contest.get("post_processor")
    post_processor = post_processor() if post_processor else None

    return _ContestGridSearchContext(
        paths=paths,
        config=config,
        data_schema=data_schema,
        post_processor=post_processor,
        metric_calculator=metric_calculator,
        test_pipeline=test_pipeline,
        load_regression_gridsearch_results=load_regression_gridsearch_results,
        metadata_handler=metadata_handler,
        parameter_grid_fn=parameter_grid_fn,
        feature_cache_loader=feature_cache_loader,
    )
