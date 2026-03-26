"""JSON loading and saving utilities."""

import json

from pathlib import Path
from typing import Any, Optional, Type, Union

from layers.layer_0_core.level_0 import get_logger, DataLoadError, DataProcessingError, ensure_dir
from level_3 import validate_path_is_file

logger = get_logger(__name__)


def load_json_raw(path: Union[str, Path]) -> Any:
    """
    Load JSON without validation.
    
    Args:
        path: Path to JSON file
        
    Returns:
        Parsed JSON data
    """
    with open(Path(path), 'r', encoding='utf-8') as f:
        return json.load(f)


def load_json(
    path: Union[str, Path],
    *,
    expected_type: Optional[Type] = None,
    file_type: str = "JSON",
) -> Any:
    """
    Load and validate JSON file.
    
    Args:
        path: Path to JSON file
        expected_type: Optional type to validate loaded data against
        file_type: Description for error messages (default: "JSON")
        
    Returns:
        Parsed JSON data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        DataLoadError: If JSON cannot be parsed
        ValueError: If data type doesn't match expected_type
        
    Example:
        >>> config = load_json('config.json', expected_type=dict)
        >>> data = load_json('data.json')
    """
    try:
        path_obj = validate_path_is_file(path, name=file_type)
    except Exception as e:
        raise DataLoadError(f"Invalid {file_type} path: {e}")

    try:
        with open(path_obj, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        raise DataLoadError(f"Failed to load {file_type} {path_obj}: {e}")

    if expected_type and not isinstance(data, expected_type):
        raise ValueError(
            f"{file_type} must contain {expected_type.__name__}, got {type(data).__name__}"
        )

    logger.debug(f"Loaded {file_type}: {path_obj}")
    return data


def save_json(
    data: Any,
    path: Union[str, Path],
    *,
    indent: int = 2,
) -> None:
    """
    Save data as JSON file.
    
    Args:
        data: Data to save (must be JSON-serializable)
        path: Path where to save file
        indent: JSON indentation level (default: 2)
        
    Raises:
        DataProcessingError: If save fails
        
    Example:
        >>> save_json({'result': 0.95, 'model': 'bert'}, 'output.json')
    """
    path = Path(path)
    try:
        ensure_dir(path.parent)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        logger.debug(f"Saved JSON: {path}")
    except Exception as e:
        raise DataProcessingError(f"Failed to save JSON {path}: {e}")