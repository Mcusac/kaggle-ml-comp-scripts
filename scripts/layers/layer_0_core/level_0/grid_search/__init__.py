"""Parameter space and combinatorics for grid search."""

from .combinatorics import generate_power_set
from .constants import (
    BEST_HYPERPARAMETERS_FILE,
    BEST_VARIANT_FILE_DATASET,
    DATASET_TYPE_FULL,
    DATASET_TYPE_SPLIT,
    DEFAULT_CLEANUP_INTERVAL,
    DEFAULT_KEEP_TOP_VARIANTS,
    FOCUSED_SEARCH_TYPES,
    GRID_SEARCH_TYPE_DATASET,
    GRID_SEARCH_TYPE_FIELD_DATASET,
    GRID_SEARCH_TYPE_FIELD_HYPERPARAMETER,
    GRID_SEARCH_TYPE_HYPERPARAMETER,
    MODEL_DIR_DATASET_GRID_SEARCH,
    MODEL_DIR_HYPERPARAMETER_GRID_SEARCH,
    RESULTS_FILE_GRIDSEARCH,
    SEARCH_TYPE_DEFAULTS,
    SEARCH_TYPE_FOCUSED_IN_DEPTH,
    SEARCH_TYPE_FOCUSED_THOROUGH,
    SEARCH_TYPE_IN_DEPTH,
    SEARCH_TYPE_QUICK,
    SEARCH_TYPE_THOROUGH,
    VALID_HYPERPARAMETER_SEARCH_TYPES,
)
from .grid_engine import build_parameter_grid, merge_focused_ranges_into_base_grid
from .param_space import calculate_total_combinations, generate_param_combinations
from .result_builders import create_error_result_dict, create_result_dict
from .results_payload import extract_results_list
from .result_selection import (
    filter_results,
    filter_successful_results,
    get_best_variant,
    get_top_n_variants,
    worst_case_metric_sentinel,
)
from .varied_params import resolve_varied_params

__all__ = [
    "generate_power_set",
    "GRID_SEARCH_TYPE_DATASET",
    "GRID_SEARCH_TYPE_HYPERPARAMETER",
    "SEARCH_TYPE_DEFAULTS",
    "SEARCH_TYPE_QUICK",
    "SEARCH_TYPE_IN_DEPTH",
    "SEARCH_TYPE_THOROUGH",
    "SEARCH_TYPE_FOCUSED_IN_DEPTH",
    "SEARCH_TYPE_FOCUSED_THOROUGH",
    "VALID_HYPERPARAMETER_SEARCH_TYPES",
    "FOCUSED_SEARCH_TYPES",
    "DATASET_TYPE_FULL",
    "DATASET_TYPE_SPLIT",
    "RESULTS_FILE_GRIDSEARCH",
    "GRID_SEARCH_TYPE_FIELD_DATASET",
    "GRID_SEARCH_TYPE_FIELD_HYPERPARAMETER",
    "BEST_VARIANT_FILE_DATASET",
    "BEST_HYPERPARAMETERS_FILE",
    "MODEL_DIR_DATASET_GRID_SEARCH",
    "MODEL_DIR_HYPERPARAMETER_GRID_SEARCH",
    "DEFAULT_KEEP_TOP_VARIANTS",
    "DEFAULT_CLEANUP_INTERVAL",
    "build_parameter_grid",
    "merge_focused_ranges_into_base_grid",
    "calculate_total_combinations",
    "generate_param_combinations",
    "get_best_variant",
    "get_top_n_variants",
    "filter_successful_results",
    "worst_case_metric_sentinel",
    "filter_results",
    "create_result_dict",
    "create_error_result_dict",
    "extract_results_list",
    "resolve_varied_params",
]
