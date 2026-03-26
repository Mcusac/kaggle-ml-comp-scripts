"""Grid search engine utilities."""

from typing import Any, Dict, List


def build_parameter_grid(
    defaults: Dict[str, Any],
    varied_params: Dict[str, List[Any]],
) -> Dict[str, List[Any]]:
    """
    Build a parameter grid from defaults and varied parameters.

    Each default value becomes a single-element list.
    Varied parameters override defaults.
    """
    base_grid = {param: [value] for param, value in defaults.items()}
    return {**base_grid, **varied_params}


def merge_focused_ranges_into_base_grid(
    base_grid: Dict[str, List[Any]],
    focused_ranges: Dict[str, List[Any]],
) -> Dict[str, List[Any]]:
    """
    Merge focused parameter ranges into an existing base grid.
    """
    return {
        param: focused_ranges.get(param, base_grid[param])
        for param in base_grid
    }