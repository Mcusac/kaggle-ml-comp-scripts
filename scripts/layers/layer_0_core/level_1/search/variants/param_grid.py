"""
Generic parameter grid resolution.
"""

from typing import Any, Dict, List

from layers.layer_0_core.level_0 import ConfigValidationError, get_logger

logger = get_logger(__name__)


def resolve_param_grid(
    grid_config: Dict[str, Any],
    quick_mode: bool = False,
) -> Dict[str, List]:
    """
    Resolve a parameter grid from config.

    Resolution order:
      1. quick_param_grid (if quick_mode)
      2. param_grid
      3. error

    Framework-level: no domain assumptions.
    """

    if quick_mode and "quick_param_grid" in grid_config:
        logger.debug("Quick mode: resolved quick_param_grid")
        return grid_config["quick_param_grid"].copy()

    if "param_grid" in grid_config:
        return grid_config["param_grid"].copy()

    raise ConfigValidationError(
        "No parameter grid found. "
        "Expected: 'quick_param_grid' or 'param_grid'."
    )