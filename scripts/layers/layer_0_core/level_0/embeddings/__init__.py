"""Base utilities for working with embeddings."""

from .alignment import align_embeddings
from .id_ops import find_common_ids
from .normalize import normalize_embedding_type
from .path_resolver import resolve_embedding_base_path

__all__ = [
    "align_embeddings",
    "find_common_ids",
    "normalize_embedding_type",
    "resolve_embedding_base_path",
]