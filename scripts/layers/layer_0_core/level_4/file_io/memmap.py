"""Memory-mapped array utilities for large datasets.

Memory mapping allows efficient loading of large arrays without fully
loading them into RAM. Useful for datasets larger than available memory.
"""

import numpy as np
import json

from pathlib import Path
from typing import Tuple, Optional, Dict, Any

from layers.layer_0_core.level_0 import get_logger, DataLoadError, DataProcessingError, DataValidationError, ensure_dir
from layers.layer_0_core.level_3 import validate_path_is_file

_logger = get_logger(__name__)

# Default threshold for using memmap (2GB)
MEMMAP_THRESHOLD_MB = 2048.0


def should_use_memmap(
    shape: Tuple[int, ...],
    dtype: np.dtype = np.float32,
    threshold_mb: float = MEMMAP_THRESHOLD_MB,
) -> bool:
    """
    Determine if array should use memory-mapped file.
    
    Args:
        shape: Array shape.
        dtype: Array dtype (default: float32).
        threshold_mb: Memory threshold in MB (default: 2048).
        
    Returns:
        True if array size exceeds threshold.
        
    Example:
        >>> should_use_memmap((1000000, 1000), dtype=np.float32)
        True
    """
    size_bytes = np.prod(shape) * dtype.itemsize
    size_mb = size_bytes / (1024 * 1024)
    return size_mb > threshold_mb


def create_memmap(
    path: Path,
    shape: Tuple[int, ...],
    dtype: np.dtype = np.float32,
    mode: str = 'w+',
) -> np.memmap:
    """
    Create a memory-mapped array.
    
    Args:
        path: Path to memmap file.
        shape: Array shape.
        dtype: Array dtype (default: float32).
        mode: Memmap mode ('r'=read, 'r+'=read-write, 'w+'=create, 'c'=copy-on-write).
        
    Returns:
        Memory-mapped array.
        
    Raises:
        DataProcessingError: If creation fails.
    """
    try:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        memmap = np.memmap(path, dtype=dtype, mode=mode, shape=shape)
        _logger.debug(f"Created memmap: {path} (shape={shape}, dtype={dtype})")
        return memmap
    except Exception as e:
        raise DataProcessingError(f"Failed to create memmap {path}: {e}")


def load_memmap(path: Path, mode: str = 'r') -> np.memmap:
    """
    Load a memory-mapped array (NumPy .npy format via np.load with mmap_mode).

    Validates path with level_3.validate_path_is_file before load (consistent with other file_io loaders).

    Args:
        path: Path to memmap file.
        mode: Memmap mode ('r'=read, 'r+'=read-write, 'c'=copy-on-write).

    Returns:
        Memory-mapped array.

    Raises:
        DataValidationError: If path is invalid.
        DataLoadError: If memmap file doesn't exist or cannot be loaded.
    """
    try:
        path_obj = validate_path_is_file(path, name="Memmap file")
    except Exception as e:
        raise DataValidationError(f"Invalid memmap path: {e}") from e

    try:
        return np.load(path_obj, mmap_mode=mode)
    except Exception as e:
        raise DataLoadError(f"Failed to load memmap {path_obj}: {e}") from e


def save_memmap_with_metadata(
    array: np.ndarray,
    path: Path,
    metadata: Optional[Dict[str, Any]] = None,
    dtype: np.dtype = np.float32,
) -> Path:
    """
    Save array as memmap with metadata file.
    
    Saves array as memory-mapped file and creates a JSON metadata file
    containing shape, dtype, and any additional metadata. This enables
    validation and dimension checking without loading the full array.
    
    Args:
        array: Array to save
        path: Path for memmap file
        metadata: Optional metadata dict (shape, dtype, etc. auto-added)
        dtype: Data type for memmap (default: float32)
        
    Returns:
        Path to saved memmap file
        
    Raises:
        DataProcessingError: If save fails
        
    Example:
        >>> arr = np.random.randn(10000, 1000)
        >>> path = save_memmap_with_metadata(arr, Path('large_array.npy'))
    """
    try:
        path = Path(path)
        ensure_dir(path.parent)
        
        # Ensure correct dtype
        if array.dtype != dtype:
            array = array.astype(dtype)
        
        # Save as memmap
        memmap = np.memmap(path, dtype=dtype, mode='w+', shape=array.shape)
        memmap[:] = array[:]
        memmap.flush()
        
        # Prepare metadata
        if metadata is None:
            metadata = {}
        
        # Auto-add shape, dtype, and size
        metadata['shape'] = list(array.shape)
        metadata['dtype'] = str(dtype)
        size_bytes = np.prod(array.shape) * dtype.itemsize
        metadata['size_mb'] = size_bytes / (1024 * 1024)
        
        # Save metadata
        metadata_path = path.with_suffix(path.suffix + '.meta')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        _logger.debug(
            f"Saved memmap with metadata: {path} "
            f"(shape={array.shape}, {metadata['size_mb']:.1f}MB)"
        )
        
        return path
    
    except Exception as e:
        raise DataProcessingError(f"Failed to save memmap {path}: {e}")


def load_memmap_with_metadata(
    path: Path,
    mode: str = 'r',
) -> Tuple[np.memmap, Dict[str, Any]]:
    """
    Load memmap with metadata.

    Validates path with level_3.validate_path_is_file before load (consistent with other file_io loaders).

    Loads memory-mapped array and its associated metadata file.
    Validates that the memmap file matches the metadata.

    Args:
        path: Path to memmap file
        mode: Memmap mode ('r'=read, 'r+'=read-write, 'c'=copy-on-write)

    Returns:
        Tuple of (memmap_array, metadata_dict)

    Raises:
        DataValidationError: If path is invalid.
        DataLoadError: If memmap or metadata file doesn't exist or metadata is invalid.

    Example:
        >>> memmap, metadata = load_memmap_with_metadata(Path('large_array.npy'))
        >>> print(f"Shape: {metadata['shape']}, Size: {metadata['size_mb']:.1f}MB")
    """
    try:
        path_obj = validate_path_is_file(path, name="Memmap file")
    except Exception as e:
        raise DataValidationError(f"Invalid memmap path: {e}") from e

    try:
        # Load metadata
        metadata_path = path_obj.with_suffix(path_obj.suffix + '.meta')
        if not metadata_path.exists():
            raise DataLoadError(f"Metadata file not found: {metadata_path}")
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)

        # Extract shape and dtype from metadata
        shape = tuple(metadata['shape'])
        dtype_str = metadata.get('dtype', 'float32')

        # Convert dtype string to numpy dtype
        try:
            dtype = np.dtype(dtype_str)
        except Exception as e:
            raise DataLoadError(
                f"Invalid dtype in metadata for {path_obj}: {dtype_str}. Error: {e}"
            ) from e

        # Load memmap
        memmap = np.memmap(path_obj, dtype=dtype, mode=mode, shape=shape)

        _logger.debug(
            f"Loaded memmap with metadata: {path_obj} "
            f"(shape={shape}, {metadata.get('size_mb', 0):.1f}MB)"
        )
        
        return memmap, metadata

    except (DataValidationError, DataLoadError):
        raise
    except Exception as e:
        raise DataLoadError(f"Failed to load memmap {path_obj}: {e}") from e