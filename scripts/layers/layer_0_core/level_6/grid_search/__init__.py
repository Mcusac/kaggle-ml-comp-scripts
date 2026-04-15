"""Grid search infrastructure: base class, result handlers, variant grid."""

from layers.layer_0_core.level_5 import (
    analyze_results_for_focused_grid,
    cleanup_checkpoints,
    cleanup_grid_search_checkpoints_retroactive,
    extract_parameter_ranges,
    extract_top_results,
    get_focused_parameter_grid,
    get_next_variant_index,
    load_completed_variants_helper,
    load_raw_results,
    save_variant_result_helper,
)
from .grid_search_base import GridSearchBase
from .grid_search_results import auto_detect_grid_search_results, calculate_focused_grid_size
from .result_handlers import (
    handle_dataset_grid_search_result,
    handle_hyperparameter_grid_search_result,
    handle_regression_grid_search_result,
)
from .variant_cleanup_runner import get_completed_count, run_final_cleanup, run_variant_cleanup
from .variant_grid import (
    create_regression_variant_key_from_result,
    create_variant_key,
    create_variant_key_from_result,
    create_variant_specific_data,
    get_default_hyperparameters,
)

__all__ = [
    "GridSearchBase",
    "auto_detect_grid_search_results",
    "calculate_focused_grid_size",
    "get_completed_count",
    "run_final_cleanup",
    "run_variant_cleanup",
    "handle_hyperparameter_grid_search_result",
    "handle_dataset_grid_search_result",
    "handle_regression_grid_search_result",
    "get_focused_parameter_grid",
    "load_raw_results",
    "extract_top_results",
    "extract_parameter_ranges",
    "analyze_results_for_focused_grid",
    "create_variant_specific_data",
    "create_variant_key",
    "create_variant_key_from_result",
    "create_regression_variant_key_from_result",
    "get_default_hyperparameters",
    "cleanup_grid_search_checkpoints_retroactive",
    "cleanup_checkpoints",
    "load_completed_variants_helper",
    "get_next_variant_index",
    "save_variant_result_helper",
]
