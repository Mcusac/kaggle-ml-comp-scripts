"""Generic grid search context builder for contest pipelines."""

from typing import Any, Callable, Optional

from layers.layer_1_competition.level_0_infra.level_0.context_types import (
    ContestGridSearchContext,
)
from layers.layer_1_competition.level_0_infra.level_1.registry.contest_registry import (
    get_contest,
)


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

    return ContestGridSearchContext(
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
