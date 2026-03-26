"""Pickle-based object serialization utilities."""

import pickle

from pathlib import Path
from typing import Any, Optional, Union

from layers.layer_0_core.level_0 import get_logger, DataLoadError, DataProcessingError, DataValidationError, ensure_dir
from level_3 import validate_path_is_file

logger = get_logger(__name__)

PICKLE_HIGHEST_PROTOCOL = pickle.HIGHEST_PROTOCOL


def load_pickle_raw(path: Union[str, Path]) -> Any:
    """
    Load pickle without validation.
    
    Args:
        path: Path to pickle file
        
    Returns:
        Deserialized object
    """
    with open(Path(path), 'rb') as f:
        return pickle.load(f)


def load_pickle(path: Union[str, Path]) -> Any:
    """
    Load and deserialize pickle file.
    
    Args:
        path: Path to pickle file
        
    Returns:
        Deserialized object
        
    Raises:
        DataValidationError: If path is invalid
        DataLoadError: If pickle cannot be loaded or deserialized

    Example:
        >>> data = load_pickle('model.pkl')
    """
    try:
        path_obj = validate_path_is_file(path, name="Pickle file")
    except Exception as e:
        raise DataValidationError(f"Invalid pickle path: {e}") from e

    try:
        with open(path_obj, "rb") as f:
            return pickle.load(f)
    except Exception as e:
        raise DataLoadError(f"Failed to load pickle {path_obj}: {e}") from e


def save_pickle(
    data: Any,
    path: Union[str, Path],
    *,
    protocol: Optional[int] = None,
) -> None:
    """
    Serialize and save object as pickle file.

    Args:
        data: Object to serialize
        path: Path where to save pickle file
        protocol: If set, passed to pickle.dump (e.g. PICKLE_HIGHEST_PROTOCOL).

    Raises:
        DataProcessingError: If save fails

    Example:
        >>> save_pickle(model, 'model.pkl')
    """
    path = Path(path)
    try:
        ensure_dir(path.parent)
        with open(path, "wb") as f:
            if protocol is None:
                pickle.dump(data, f)
            else:
                pickle.dump(data, f, protocol=protocol)
        logger.debug(f"Saved pickle: {path}")
    except Exception as e:
        raise DataProcessingError(f"Failed to save pickle {path}: {e}") from e