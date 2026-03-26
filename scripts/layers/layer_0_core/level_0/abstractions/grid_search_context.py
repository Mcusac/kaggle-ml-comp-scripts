"""Protocol for grid search pipeline context. Contest layer provides implementation."""

from typing import Any, Callable, Protocol


class GridSearchContext(Protocol):
    """Context for grid search pipelines: paths, config, optional metric. Implemented by contest layer."""

    def get_paths(self) -> Any:
        """Return contest paths object."""
        ...

    def get_config(self) -> Any:
        """Return contest config object (with paths attachable)."""
        ...

    def get_metric_calculator(self) -> Callable[..., float]:
        """Return contest metric function (e.g. calc_metric). Optional; default to None."""
        ...

    def get_metadata_handler(self) -> Any:
        """Return object with get_or_create_variant_id, save_gridsearch_result, initialize_metadata_files."""
        ...

    def get_feature_cache_loader(self) -> Any:
        """Return object with find_feature_cache(filename) -> Path, load_features(path) -> tuple."""
        ...

    def get_parameter_grid_fn(self) -> Callable[..., Any]:
        """Return (model_type, search_type) -> param_grid dict for regression grid search."""
        ...
