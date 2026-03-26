"""CAFA-specific embedding loading using contest paths and generic component loaders."""

import numpy as np

from pathlib import Path
from typing import Tuple, Optional

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import load_ids_file, build_embedding_error_message, load_embeddings_file

from layers.layer_1_competition.level_1_impl.level_cafa.level_0 import (
    load_t5_rds, 
    load_t5_qs,
    get_embedding_paths,
    resolve_base_path,
    resolve_embedding_paths,
    normalize_embedding_type_cafa,
)

logger = get_logger(__name__)


def load_embedding_data(
    embedding_type: str,
    datatype: str = "train",
    use_memmap: bool = None,
    base_path: Optional[Path] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load embeddings from numpy files using CAFA-specific paths.

    Supports full array and memory-mapped loading, float32 conversion,
    and T5 .qs/.rds handling.
    """
    embedding_type = normalize_embedding_type_cafa(embedding_type)
    base_path = resolve_base_path(embedding_type, base_path)
    use_memmap = use_memmap if use_memmap is not None else True

    if embedding_type in ["t5", "prot_t5_xl"]:
        return load_t5_embeddings(base_path, datatype, use_memmap)

    return load_numpy_embeddings(
        embedding_type, datatype, base_path, use_memmap
    )


def load_numpy_embeddings(
    embedding_type: str,
    datatype: str,
    base_path: Path,
    use_memmap: bool,
) -> Tuple[np.ndarray, np.ndarray]:
    """Load numpy embeddings from files using CAFA path resolution."""
    embedding_paths, cafa6_embeddings_dir = get_embedding_paths()
    ids_path, embeddings_path, checked_paths = resolve_embedding_paths(
        embedding_type, datatype, base_path, cafa6_embeddings_dir
    )

    try:
        ids = load_ids_file(ids_path)
        embeds = load_embeddings_file(
            embeddings_path, embedding_type, datatype, use_memmap
        )
        return embeds, ids
    except FileNotFoundError as e:
        error_msg = build_embedding_error_message(
            embedding_type, datatype, base_path, checked_paths
        )
        raise FileNotFoundError(error_msg) from e


def load_t5_embeddings(
    base_path: Path,
    datatype: str,
    use_memmap: bool,
) -> Tuple[np.ndarray, np.ndarray]:
    """Load T5 embeddings from .qs or .rds files."""
    qs_path = base_path / f"T5_{datatype}_features.qs"
    if qs_path.exists():
        return load_t5_qs(qs_path, datatype, use_memmap)

    rds_path = base_path / f"CAFA5_{datatype}_t5embeds.rds"
    if rds_path.exists():
        return load_t5_rds(rds_path, datatype, use_memmap)

    raise FileNotFoundError(
        f"T5 embedding files not found. Checked:\n"
        f"  - {qs_path}\n"
        f"  - {rds_path}"
    )
