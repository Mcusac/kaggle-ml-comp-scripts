"""Grid search results detection and focused grid size."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from layers.layer_0_core.level_0 import calculate_total_combinations, get_logger, is_kaggle
from layers.layer_0_core.level_1 import get_transformer_hyperparameter_grid, resolve_environment_path
from layers.layer_0_core.level_5 import get_focused_parameter_grid

logger = get_logger(__name__)


def calculate_focused_grid_size(
    base_search_type: str,
    previous_results_file: str,
    top_n_results: int = 10,
    range_expansion_factor: float = 1.5,
    min_values_per_param: int = 2,
) -> Tuple[Dict[str, List[Any]], int, Optional[int]]:
    """
    Calculate focused grid size before running search.

    Args:
        base_search_type: Type of search (e.g., 'hyperparameter').
        previous_results_file: Path to prior grid search results JSON.
        top_n_results: Number of top results to use for focused range.
        range_expansion_factor: Factor to expand parameter ranges.
        min_values_per_param: Minimum values per parameter.

    Returns:
        Tuple of (focused_param_grid, focused_combinations, base_combinations).
    """
    base_grid = get_transformer_hyperparameter_grid(base_search_type)
    base_combinations = calculate_total_combinations(base_grid)
    focused_grid = get_focused_parameter_grid(
        base_search_type=base_search_type,
        previous_results_file=previous_results_file,
        top_n_results=top_n_results,
        range_expansion_factor=range_expansion_factor,
        min_values_per_param=min_values_per_param,
    )
    focused_combinations = calculate_total_combinations(focused_grid)
    return focused_grid, focused_combinations, base_combinations


def auto_detect_grid_search_results(model_name: Optional[str] = None) -> str:
    """Auto-detect grid search results files. Raises FileNotFoundError if none found."""
    checked_paths = []
    if is_kaggle():
        base_dir = Path("/kaggle/input/csiro-metadata")
        if model_name:
            model_specific_dir = base_dir / model_name
            metadata_file = model_specific_dir / "metadata.json"
            checked_paths.append(str(metadata_file))
            if metadata_file.exists():
                logger.info(
                    "Found model metadata in model-specific folder: %s",
                    metadata_file,
                )
                return str(metadata_file)
        working_unified_hyperparam = Path(
            "/kaggle/working/output/hyperparameter_grid_search/gridsearch_results.json"
        )
        working_unified_dataset = Path(
            "/kaggle/working/output/dataset_grid_search/gridsearch_results.json"
        )
        checked_paths.append(str(working_unified_hyperparam))
        checked_paths.append(str(working_unified_dataset))
        if working_unified_hyperparam.exists():
            logger.info(
                "Found in-progress unified hyperparameter grid search: %s",
                working_unified_hyperparam,
            )
            return str(working_unified_hyperparam)
        if working_unified_dataset.exists():
            logger.info(
                "Found in-progress unified dataset grid search: %s",
                working_unified_dataset,
            )
            return str(working_unified_dataset)
    else:
        unified_hyperparam_file = resolve_environment_path(
            "output/hyperparameter_grid_search/gridsearch_results.json"
        )
        unified_dataset_file = resolve_environment_path(
            "output/dataset_grid_search/gridsearch_results.json"
        )
        checked_paths.append(str(unified_hyperparam_file))
        checked_paths.append(str(unified_dataset_file))
        if unified_hyperparam_file.exists():
            logger.info(
                "Found unified hyperparameter grid search results: %s",
                unified_hyperparam_file,
            )
            return str(unified_hyperparam_file)
        if unified_dataset_file.exists():
            logger.info(
                "Found unified dataset grid search results: %s",
                unified_dataset_file,
            )
            return str(unified_dataset_file)
    error_msg = "No grid search results found.\nChecked paths (in order):\n"
    for idx, path in enumerate(checked_paths, 1):
        error_msg += f"  {idx}. {path}\n"
    error_msg += (
        "\nNext steps:\n"
        "  - Upload grid search results to Kaggle input dataset\n"
        "  - Or run grid search pipeline to generate new results\n"
    )
    raise FileNotFoundError(error_msg)
