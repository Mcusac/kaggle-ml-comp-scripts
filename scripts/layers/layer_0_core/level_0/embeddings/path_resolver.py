"""Generic embedding path resolution."""

from pathlib import Path
from typing import Dict, Optional


def resolve_embedding_base_path(
    embedding_type: str,
    base_path: Optional[Path],
    paths_config: Dict[str, Path],
) -> Path:
    """
    Resolve base path for an embedding type.

    Args:
        embedding_type: Key in paths_config (e.g. 'esm2_650m')
        base_path: Override if provided
        paths_config: Dict mapping embedding_type -> base Path

    Returns:
        Base path for this embedding type

    Raises:
        ValueError: If embedding_type not in paths_config and base_path is None
    """
    if base_path is not None:
        return base_path
    if embedding_type in paths_config:
        return paths_config[embedding_type]
    valid = ", ".join(sorted(paths_config.keys()))
    raise ValueError(
        f"Unknown embedding_type: {embedding_type}. Choose from: [{valid}]"
    )
