"""YAML configuration file loading and saving utilities."""

import yaml

from pathlib import Path
from typing import Any, Union

from layers.layer_0_core.level_0 import get_logger, DataLoadError, DataProcessingError, DataValidationError, ensure_dir
from layers.layer_0_core.level_3 import validate_path_is_file

_logger = get_logger(__name__)


def load_yaml_raw(path: Union[str, Path]) -> Any:
    """
    Load YAML without validation.
    
    Args:
        path: Path to YAML file
        
    Returns:
        Parsed YAML data
    """
    with open(Path(path), 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_yaml(path: Union[str, Path]) -> Any:
    """
    Load and parse YAML file safely.
    
    Args:
        path: Path to YAML file
        
    Returns:
        Parsed YAML data (typically dict or list)
        
    Raises:
        DataValidationError: If path is invalid
        DataLoadError: If YAML cannot be parsed

    Example:
        >>> config = load_yaml('config.yaml')
        >>> print(config['learning_rate'])
    """
    try:
        path_obj = validate_path_is_file(path, name="YAML file")
    except Exception as e:
        raise DataValidationError(f"Invalid YAML path: {e}") from e

    try:
        with open(path_obj, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        raise DataLoadError(f"Failed to load YAML {path_obj}: {e}") from e


def save_yaml(data: Any, path: Union[str, Path]) -> None:
    """
    Save data as YAML file.
    
    Args:
        data: Data to save (typically dict or list)
        path: Path where to save YAML file
        
    Raises:
        DataProcessingError: If save fails
        
    Example:
        >>> config = {'learning_rate': 0.001, 'batch_size': 32}
        >>> save_yaml(config, 'config.yaml')
    """
    path = Path(path)
    try:
        ensure_dir(path.parent)
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, default_flow_style=False)
        _logger.debug(f"Saved YAML: {path}")
    except Exception as e:
        raise DataProcessingError(f"Failed to save YAML {path}: {e}")