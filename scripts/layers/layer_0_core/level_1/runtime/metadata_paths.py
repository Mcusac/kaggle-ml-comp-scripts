"""Metadata path resolution utilities."""

from pathlib import Path

from layers.layer_0_core.level_0 import get_logger

logger = get_logger(__name__)


def find_metadata_candidates(model_path: Path) -> list[Path]:
    """
    Find candidate paths for model metadata file.

    Args:
        model_path: Model path (file or directory)

    Returns:
        List of candidate metadata file paths
    """
    metadata_candidates = []
    if model_path.is_dir():
        # Directory: check inside the directory
        metadata_candidates.append(model_path / 'model_metadata.json')
        metadata_candidates.append(model_path.parent / 'model_metadata.json')
    else:
        # File: check in parent directory
        metadata_candidates.append(model_path.parent / 'model_metadata.json')
        metadata_candidates.append(model_path.parent.parent / 'model_metadata.json')

    return metadata_candidates

