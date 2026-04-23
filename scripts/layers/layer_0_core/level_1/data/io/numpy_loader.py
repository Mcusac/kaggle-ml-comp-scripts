"""Load NumPy embeddings and build diagnostic error messages."""

import numpy as np

from pathlib import Path

from layers.layer_0_core.level_0 import get_logger

_logger = get_logger(__name__)


def build_embedding_error_message(
    embedding_type: str,
    datatype: str,
    base_path: Path,
    checked_paths: list
) -> str:
    """
    Build comprehensive error message for embedding loading failures.

    Args:
        embedding_type: Embedding type
        datatype: 'train' or 'test'
        base_path: Base path that was checked
        checked_paths: List of (structure_type, ids_path, embeddings_path) tuples

    Returns:
        Error message string
    """
    error_msg = f"Could not load {embedding_type} embeddings for {datatype}.\n\n"
    error_msg += "Checked paths:\n"

    for structure_type, checked_ids_path, checked_embeddings_path in checked_paths:
        error_msg += f"  [{structure_type}]\n"
        error_msg += f"    IDs: {checked_ids_path} {'✓' if checked_ids_path.exists() else '✗'}\n"
        error_msg += f"    Embeddings: {checked_embeddings_path} {'✓' if checked_embeddings_path.exists() else '✗'}\n"

    error_msg += f"\nDirectory diagnostics:\n"
    error_msg += f"  Base directory: {base_path} {'✓ exists' if base_path.exists() else '✗ does not exist'}\n"
    if base_path.exists():
        try:
            files = list(base_path.iterdir())
            if files:
                error_msg += f"  Files in base directory ({len(files)} found):\n"
                for f in sorted(files)[:10]:
                    error_msg += f"    - {f.name}\n"
                if len(files) > 10:
                    error_msg += f"    ... and {len(files) - 10} more files\n"
        except PermissionError:
            error_msg += f"  Cannot list files (permission denied)\n"

    return error_msg


def load_ids_file(ids_path: Path) -> np.ndarray:
    """Load IDs file."""
    if not ids_path.exists():
        raise FileNotFoundError(f"ID file not found: {ids_path}")
    return np.load(ids_path)


def load_embeddings_file(
    embeddings_path: Path,
    embedding_type: str,
    datatype: str,
    use_memmap: bool
) -> np.ndarray:
    """Load embeddings file (memmap or full array)."""
    if not embeddings_path.exists():
        raise FileNotFoundError(f"Embeddings file not found: {embeddings_path}")

    if use_memmap:
        embeds = np.load(embeddings_path, mmap_mode='r')
        _logger.info(f"Loaded {embedding_type} {datatype} as memmap: {embeds.shape} (dtype: {embeds.dtype})")
    else:
        embeds = np.load(embeddings_path)
        if embeds.dtype != np.float32:
            embeds = embeds.astype(np.float32)
        _logger.info(f"Loaded {embedding_type} {datatype}: {embeds.shape} (dtype: {embeds.dtype})")

    return embeds
