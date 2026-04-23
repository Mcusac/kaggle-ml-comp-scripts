"""Environment and directory setup utilities for grid search."""

from pathlib import Path
from typing import Tuple, Any, Union, Dict

from layers.layer_0_core.level_0 import ensure_dir, ConfigValidationError, get_logger
from layers.layer_0_core.level_1 import get_device, get_device_info

_logger = get_logger(__name__)


def setup_grid_search_environment(
    config: Union[Any, Dict[str, Any]],
    grid_search_type_fn
) -> Tuple[Any, Path, Path, Any]:
    """
    Set up grid search environment.

    Args:
        config: Configuration object or dict
        grid_search_type_fn: Function that returns grid search type string

    Returns:
        Tuple of (device, base_model_dir, grid_search_dir, device_info).
    """
    # Get paths from config (set by pipeline from contest_context)
    paths = getattr(config, 'paths', None)
    if paths is None or not (
        hasattr(paths, 'get_output_dir')
        and hasattr(paths, 'get_models_base_dir')
    ):
        raise ConfigValidationError(
            "config.paths is required with get_output_dir() and "
            "get_models_base_dir(); use contest_context"
        )

    # Device setup
    device = get_device('auto')
    device_info = get_device_info()
    _logger.info(f"Device info: {device_info}")

    # Call grid_search_type_fn ONCE
    grid_search_type = grid_search_type_fn()

    # Normalize base model directory
    base_model_dir = normalize_base_model_dir(
        config,
        grid_search_type,
        paths
    )

    # Create grid search output directory
    grid_search_dir = create_grid_search_dir(
        config,
        grid_search_type,
        paths
    )

    return device, base_model_dir, grid_search_dir, device_info


def apply_memory_optimizations(config: Union[Any, Dict[str, Any]]) -> None:
    """
    Apply memory optimization settings for grid search.

    Reduces num_workers and disables pin_memory if configured.
    """
    if isinstance(config, dict):
        if config.get('reduce_workers_for_memory', False):
            config['num_workers'] = 0
            _logger.info("Memory optimization: Reduced num_workers to 0")
        if config.get('disable_pin_memory_for_memory', False):
            config['pin_memory'] = False
            _logger.info("Memory optimization: Disabled pin_memory")

    elif hasattr(config, 'device'):
        if getattr(config.device, 'reduce_workers_for_memory', False):
            config.device.num_workers = 0
            _logger.info("Memory optimization: Reduced num_workers to 0")

        if getattr(config.device, 'disable_pin_memory_for_memory', False):
            config.device.pin_memory = False
            _logger.info("Memory optimization: Disabled pin_memory")


def normalize_base_model_dir(
    config: Union[Any, Dict[str, Any]],
    grid_search_type: str,
    paths: Any
) -> Path:
    """
    Normalize base model directory to prevent path nesting.
    """
    base_model_dir = paths.get_models_base_dir()

    # Check if base_model_dir ends with grid_search_type
    if base_model_dir.name == grid_search_type:
        base_model_dir = base_model_dir.parent
        _logger.info(
            f"Normalized base model directory: {base_model_dir} "
            f"(removed trailing '{grid_search_type}')"
        )

    return base_model_dir


def create_grid_search_dir(
    config: Union[Any, Dict[str, Any]],
    grid_search_type: str,
    paths: Any
) -> Path:
    """
    Create grid search output directory.
    """
    dataset_type = 'split'

    if isinstance(config, dict):
        dataset_type = config.get('dataset_type', 'split')

    elif hasattr(config, 'data') and hasattr(config.data, 'dataset_type'):
        dataset_type = config.data.dataset_type

    grid_search_dir = paths.get_output_dir() / f"{grid_search_type}_{dataset_type}"

    ensure_dir(grid_search_dir)

    return grid_search_dir
