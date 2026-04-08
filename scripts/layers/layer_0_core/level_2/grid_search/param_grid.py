"""
Keyed parameter grid resolution.

Supports per-key overrides (task, head, domain, etc).
"""

from typing import Any, Dict, List, Optional

from level_0 import get_logger
from level_1 import resolve_param_grid

logger = get_logger(__name__)


def resolve_keyed_param_grid(
    grid_config: Dict[str, Any],
    key: Optional[str] = None,
    quick_mode: bool = False,
    keyed_grids_field: str = "param_grids",
) -> Dict[str, List]:
    """
    Resolve a parameter grid with optional keyed overrides.

    Resolution order:
      1. quick_param_grid (if quick_mode)
      2. keyed grid (if key present)
      3. base param_grid

    Args:
        grid_config: Config dictionary
        key: Task / domain / head identifier
        quick_mode: Prefer quick grid
        keyed_grids_field: Field name for keyed grids
    """

    # Quick mode still wins
    if quick_mode and "quick_param_grid" in grid_config:
        logger.debug("Quick mode: resolved quick_param_grid")
        return grid_config["quick_param_grid"].copy()

    # Keyed override
    if (
        key
        and keyed_grids_field in grid_config
        and key in grid_config[keyed_grids_field]
    ):
        logger.debug("Resolved keyed grid for '%s'", key)
        return grid_config[keyed_grids_field][key].copy()

    # Fallback to base
    return resolve_param_grid(grid_config, quick_mode=False)