"""Auto-generated package exports."""


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

from .grid_engine import (
    build_parameter_grid,
    merge_focused_ranges_into_base_grid,
)

from .param_space import (
    calculate_total_combinations,
    generate_param_combinations,
)

from .result_builders import (
    create_error_result_dict,
    create_result_dict,
)

from .result_selection import (
    filter_results,
    filter_successful_results,
    get_best_variant,
    get_top_n_variants,
    worst_case_metric_sentinel,
)

from .results_payload import extract_results_list

from .varied_params import resolve_varied_params

__all__ = [
    "BEST_HYPERPARAMETERS_FILE",
    "BEST_VARIANT_FILE_DATASET",
    "DATASET_TYPE_FULL",
    "DATASET_TYPE_SPLIT",
    "DEFAULT_CLEANUP_INTERVAL",
    "DEFAULT_KEEP_TOP_VARIANTS",
    "FOCUSED_SEARCH_TYPES",
    "GRID_SEARCH_TYPE_DATASET",
    "GRID_SEARCH_TYPE_FIELD_DATASET",
    "GRID_SEARCH_TYPE_FIELD_HYPERPARAMETER",
    "GRID_SEARCH_TYPE_HYPERPARAMETER",
    "MODEL_DIR_DATASET_GRID_SEARCH",
    "MODEL_DIR_HYPERPARAMETER_GRID_SEARCH",
    "RESULTS_FILE_GRIDSEARCH",
    "SEARCH_TYPE_DEFAULTS",
    "SEARCH_TYPE_FOCUSED_IN_DEPTH",
    "SEARCH_TYPE_FOCUSED_THOROUGH",
    "SEARCH_TYPE_IN_DEPTH",
    "SEARCH_TYPE_QUICK",
    "SEARCH_TYPE_THOROUGH",
    "VALID_HYPERPARAMETER_SEARCH_TYPES",
    "build_parameter_grid",
    "calculate_total_combinations",
    "create_error_result_dict",
    "create_result_dict",
    "extract_results_list",
    "filter_results",
    "filter_successful_results",
    "generate_param_combinations",
    "generate_power_set",
    "get_best_variant",
    "get_top_n_variants",
    "merge_focused_ranges_into_base_grid",
    "resolve_varied_params",
    "worst_case_metric_sentinel",
]
