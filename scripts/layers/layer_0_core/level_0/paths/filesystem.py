"""Pure filesystem path utilities.

This module provides basic path operations that don't depend on
execution environment or application context.
"""

from pathlib import Path
from typing import Union


def ensure_dir(dirpath: Union[str, Path]) -> Path:
    """
    Ensure a directory exists, creating it (with parents) if necessary.

    This is idempotent: safe to call even if the directory already exists.

    Args:
        dirpath: Directory path (string or Path object)

    Returns:
        Path object for the directory

    Raises:
        OSError: If directory creation fails (e.g., permission denied)

    Example:
        >>> output_dir = ensure_dir("output/models/experiment_1")
        >>> checkpoint_dir = ensure_dir(Path("checkpoints") / "run_42")
    """
    dirpath = Path(dirpath)
    dirpath.mkdir(parents=True, exist_ok=True)
    return dirpath


def normalize_path(path: Union[str, Path]) -> Path:
    """
    Normalize a path (resolve .., ., expand ~, make absolute).

    Args:
        path: Path to normalize

    Returns:
        Normalized Path object

    Example:
        >>> normalize_path("~/data/../models")
        PosixPath('/home/user/models')
    """
    return Path(path).expanduser().resolve()


def get_file_size_mb(path: Union[str, Path]) -> float:
    """
    Get file size in megabytes.

    Args:
        path: Path to file

    Returns:
        File size in MB

    Raises:
        FileNotFoundError: If file doesn't exist

    Example:
        >>> size = get_file_size_mb("model.pkl")
        >>> print(f"Model is {size:.2f} MB")
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return path.stat().st_size / (1024 ** 2)


def ensure_file_dir(filepath: Union[str, Path]) -> Path:
    """
    Ensure the parent directory of a file exists.

    Convenience function for ensuring a file's directory exists
    before writing the file.

    Args:
        filepath: Path to file (directory will be created)

    Returns:
        Path object for the file (not the directory)

    Example:
        >>> filepath = ensure_file_dir("output/models/v1/model.pkl")
        >>> # Now output/models/v1/ exists
        >>> save_model(model, filepath)
    """
    filepath = Path(filepath)
    ensure_dir(filepath.parent)
    return filepath
