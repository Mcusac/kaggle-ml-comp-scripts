"""Parameter space utilities for grid search."""

import itertools

from typing import Dict, List, Any, Iterator


def calculate_total_combinations(param_grid: Dict[str, List[Any]]) -> int:
    """
    Calculate total number of parameter combinations from a parameter grid.

    Args:
        param_grid: Dictionary mapping parameter names to lists of possible values.

    Returns:
        Total number of combinations (product of all list lengths).
        Returns 1 if param_grid is empty.

    Raises:
        ValueError: If any parameter list is empty.
    """
    total = 1
    for param_name, values in param_grid.items():
        if not values:
            raise ValueError(
                f"Parameter '{param_name}' has empty values list. "
                f"All parameters must have at least one value."
            )
        total *= len(values)
    return total


def generate_param_combinations(
    param_grid: Dict[str, List[Any]]
) -> Iterator[Dict[str, Any]]:
    """
    Generate all parameter combinations from a grid.

    Yields dictionaries representing each unique parameter combination.

    Args:
        param_grid: Dictionary mapping parameter names to value lists

    Yields:
        Dict[str, Any]: Individual parameter combinations
    """
    if not param_grid:
        yield {}
        return

    keys = list(param_grid.keys())
    value_lists = [param_grid[k] for k in keys]

    for combination in itertools.product(*value_lists):
        yield dict(zip(keys, combination))
