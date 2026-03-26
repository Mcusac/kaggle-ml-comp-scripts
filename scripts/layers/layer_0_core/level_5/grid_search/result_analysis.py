"""Result analysis utilities for narrowing parameter grids based on previous results."""

from pathlib import Path
from typing import Any, Dict, List, Union

from level_0 import extract_results_list, get_logger, merge_focused_ranges_into_base_grid
from level_1 import get_transformer_hyperparameter_grid
from level_4 import load_json

logger = get_logger(__name__)

# Parameter types for range calculation
NUMERIC_PARAMS = {
    'learning_rate', 'batch_size', 'weight_decay', 'scheduler_factor',
    'scheduler_patience', 'early_stopping_patience', 'num_epochs'
}

CATEGORICAL_PARAMS = {
    'optimizer', 'loss_function', 'scheduler'
}


def load_raw_results(results_file: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    Load grid search results from JSON file.

    Args:
        results_file: Path to results.json file (string or Path object).

    Returns:
        List of result dictionaries.

    Raises:
        FileNotFoundError: If results file does not exist.
        ValueError: If results file format is invalid.
    """
    results_file = Path(results_file)
    if not results_file.exists():
        raise FileNotFoundError(f"Results file not found: {results_file}")

    raw = load_json(results_file)
    if not isinstance(raw, (list, dict)):
        raise ValueError(
            f"Invalid results format: expected list or dict, got {type(raw)}"
        )
    data = extract_results_list(raw)

    logger.info(f"Loaded {len(data)} results from {results_file}")
    return data


def extract_top_results(
    results: List[Dict[str, Any]],
    top_n: int = 10,
    metric_key: str = 'cv_score',
) -> List[Dict[str, Any]]:
    """
    Extract top N performing results sorted by metric.

    Args:
        results: List of result dictionaries.
        top_n: Number of top results to extract (default: 10).
        metric_key: Key to use for sorting (default: 'cv_score').

    Returns:
        List of top N result dictionaries, sorted by metric (descending).

    Raises:
        ValueError: If no valid results are found.
    """
    valid_results = [
        r for r in results
        if r.get(metric_key) is not None
        and not (
            isinstance(r.get(metric_key), float)
            and r[metric_key] != r[metric_key]  # NaN check
        )
    ]

    if not valid_results:
        raise ValueError(f"No valid results found with metric key '{metric_key}'")

    sorted_results = sorted(
        valid_results,
        key=lambda x: x.get(metric_key, -float('inf')),
        reverse=True,
    )

    top_results = sorted_results[:top_n]
    logger.info(f"Extracted top {len(top_results)} results (from {len(valid_results)} valid)")
    return top_results


def extract_parameter_ranges(
    top_results: List[Dict[str, Any]],
    range_expansion_factor: float = 1.5,
    min_values_per_param: int = 2,
) -> Dict[str, List[Any]]:
    """
    Extract focused parameter ranges from top results.

    For numeric parameters: creates a range around observed values expanded by
    range_expansion_factor. For categorical parameters: keeps only values that
    appear in the top results.

    Args:
        top_results: List of top result dictionaries.
        range_expansion_factor: Factor to expand numeric ranges (default: 1.5).
        min_values_per_param: Minimum values to retain per parameter (default: 2).

    Returns:
        Dictionary mapping parameter names to lists of focused values.

    Raises:
        ValueError: If top_results is empty or contains no hyperparameters.
    """
    if not top_results:
        raise ValueError("No top results provided")

    hyperparameters = top_results[0].get('hyperparameters', {})
    if not hyperparameters:
        raise ValueError("No hyperparameters found in results")

    focused_ranges = {}

    for param_name in hyperparameters:
        param_values = [
            r.get('hyperparameters', {}).get(param_name)
            for r in top_results
            if r.get('hyperparameters', {}).get(param_name) is not None
        ]

        if not param_values:
            logger.warning(f"No values found for parameter '{param_name}' in top results")
            continue

        if param_name in NUMERIC_PARAMS:
            focused_ranges[param_name] = _extract_numeric_range(
                param_values, range_expansion_factor, min_values_per_param, param_name
            )
        elif param_name in CATEGORICAL_PARAMS:
            focused_ranges[param_name] = _extract_categorical_values(
                param_values, min_values_per_param, param_name
            )
        else:
            unique_values = sorted(set(param_values), key=str)
            focused_ranges[param_name] = unique_values
            logger.debug(
                f"Parameter '{param_name}': unknown type, "
                f"keeping {len(unique_values)} values: {unique_values}"
            )

    return focused_ranges


def analyze_results_for_focused_grid(
    results_file: str,
    top_n: int = 10,
    range_expansion_factor: float = 1.5,
    min_values_per_param: int = 2,
    metric_key: str = 'cv_score',
) -> Dict[str, List[Any]]:
    """
    Analyze previous grid search results and return focused parameter ranges.

    Main entry point for result-based grid filtering.

    Args:
        results_file: Path to previous results.json file.
        top_n: Number of top results to analyze (default: 10).
        range_expansion_factor: Factor to expand numeric ranges (default: 1.5).
        min_values_per_param: Minimum values to retain per parameter (default: 2).
        metric_key: Key to use for sorting results (default: 'cv_score').

    Returns:
        Dictionary mapping parameter names to lists of focused values.
    """
    results = load_raw_results(results_file)
    top_results = extract_top_results(results, top_n=top_n, metric_key=metric_key)
    focused_ranges = extract_parameter_ranges(
        top_results,
        range_expansion_factor=range_expansion_factor,
        min_values_per_param=min_values_per_param,
    )
    logger.info(f"Generated focused parameter ranges for {len(focused_ranges)} parameters")
    return focused_ranges


def get_focused_parameter_grid(
    base_search_type: str,
    previous_results_file: str,
    top_n_results: int = 10,
    range_expansion_factor: float = 1.5,
    min_values_per_param: int = 2,
) -> Dict[str, List[Any]]:
    """
    Get focused parameter grid based on previous grid search results.

    Analyzes top N results from a previous search and creates a narrowed parameter
    grid around the best-performing combinations.
    """
    if base_search_type not in {"in_depth", "thorough"}:
        raise ValueError(
            f"base_search_type must be 'in_depth' or 'thorough', got {base_search_type}"
        )
    base_grid = get_transformer_hyperparameter_grid(base_search_type)
    focused_ranges = analyze_results_for_focused_grid(
        results_file=previous_results_file,
        top_n=top_n_results,
        range_expansion_factor=range_expansion_factor,
        min_values_per_param=min_values_per_param,
    )
    return merge_focused_ranges_into_base_grid(base_grid, focused_ranges)


def _extract_numeric_range(
    param_values: List[Any],
    range_expansion_factor: float,
    min_values_per_param: int,
    param_name: str,
) -> List[float]:
    """
    Build a focused numeric range from observed parameter values.

    Expands the observed min/max by range_expansion_factor and ensures at least
    min_values_per_param values are returned.

    Args:
        param_values: Observed values from top results.
        range_expansion_factor: Multiplier for range expansion.
        min_values_per_param: Minimum number of values to return.
        param_name: Parameter name used in log messages.

    Returns:
        Sorted list of focused numeric values.
    """
    numeric_values = [float(v) for v in param_values]
    min_val = min(numeric_values)
    max_val = max(numeric_values)

    range_size = max_val - min_val
    if range_size == 0:
        center = min_val
        expanded_min = center / range_expansion_factor
        expanded_max = center * range_expansion_factor
    else:
        center = (min_val + max_val) / 2
        half_range = (range_size / 2) * range_expansion_factor
        expanded_min = max(0.0, center - half_range)
        expanded_max = center + half_range

    focused_values = set(numeric_values)

    if expanded_min < min_val:
        focused_values.add(expanded_min)
    if expanded_max > max_val:
        focused_values.add(expanded_max)

    focused_list = sorted(focused_values)

    if len(focused_list) < min_values_per_param:
        step = (expanded_max - expanded_min) / (min_values_per_param - 1)
        for i in range(min_values_per_param):
            focused_values.add(expanded_min + i * step)
        focused_list = sorted(focused_values)

    logger.debug(
        f"Parameter '{param_name}': "
        f"original range [{min_val:.6f}, {max_val:.6f}], "
        f"expanded to [{expanded_min:.6f}, {expanded_max:.6f}], "
        f"{len(focused_list)} values"
    )
    return focused_list


def _extract_categorical_values(
    param_values: List[Any],
    min_values_per_param: int,
    param_name: str,
) -> List[Any]:
    """
    Return unique categorical values observed in top results.

    Args:
        param_values: Observed values from top results.
        min_values_per_param: Minimum expected count (warns if not met).
        param_name: Parameter name used in log messages.

    Returns:
        Sorted list of unique categorical values.
    """
    unique_values = sorted(set(param_values))

    if len(unique_values) < min_values_per_param:
        logger.warning(
            f"Parameter '{param_name}' has only {len(unique_values)} unique value(s) "
            f"in top results (minimum requested: {min_values_per_param})"
        )

    logger.debug(
        f"Parameter '{param_name}': "
        f"keeping {len(unique_values)} values: {unique_values}"
    )
    return unique_values
