"""JSON loading and saving utilities."""

import json
import os
import tempfile

from pathlib import Path
from typing import Any, Iterable, Optional, Type, Union

from layers.layer_0_core.level_0 import get_logger, DataLoadError, DataProcessingError, ensure_dir
from layers.layer_0_core.level_3 import validate_path_is_file

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
    ensure_ascii: bool = False,
) -> None:
    """
    Save data as JSON file.
    
    Args:
        data: Data to save (must be JSON-serializable)
        path: Path where to save file
        indent: JSON indentation level (default: 2)
        ensure_ascii: Pass through to json.dump (default False for UTF-8 files)

    Raises:
        DataProcessingError: If save fails
        
    Example:
        >>> save_json({'result': 0.95, 'model': 'bert'}, 'output.json')
    """
    path = Path(path)
    try:
        ensure_dir(path.parent)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)
        logger.debug(f"Saved JSON: {path}")
    except Exception as e:
        raise DataProcessingError(f"Failed to save JSON {path}: {e}")


def save_json_atomic(
    data: Any,
    path: Union[str, Path],
    *,
    indent: int = 2,
    ensure_ascii: bool = False,
) -> None:
    """Write JSON atomically (temp file in same directory, then replace)."""
    p = Path(path)
    try:
        ensure_dir(p.parent)
        tmp_fd: int | None = None
        tmp_path: str | None = None
        try:
            tmp_fd, tmp_path = tempfile.mkstemp(
                prefix=p.name + ".",
                suffix=".tmp",
                dir=str(p.parent),
            )
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                tmp_fd = None
                json.dump(data, f, indent=int(indent), ensure_ascii=bool(ensure_ascii))
            os.replace(str(tmp_path), str(p))
        finally:
            if tmp_fd is not None:
                try:
                    os.close(tmp_fd)
                except OSError:
                    pass
            if tmp_path is not None:
                try:
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
                except OSError:
                    pass
        logger.debug(f"Saved JSON (atomic): {p}")
    except Exception as e:
        raise DataProcessingError(f"Failed to save JSON atomically {p}: {e}")


def load_best_config_json(
    path: Union[str, Path],
    *,
    drop_keys: Optional[Iterable[str]] = None,
) -> dict[str, Any]:
    """Load a JSON object and optionally remove bookkeeping keys."""
    payload = load_json_raw(path)
    if not isinstance(payload, dict):
        raise TypeError(
            f"Expected best-config JSON object at {path}, got {type(payload).__name__}"
        )
    out = dict(payload)
    if drop_keys:
        for k in drop_keys:
            out.pop(str(k), None)
    return out