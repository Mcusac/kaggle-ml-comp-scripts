"""Embedding fusion utilities."""

import numpy as np

from typing import List, Tuple

from level_0 import align_embeddings, find_common_ids


def _align_embeddings_to_common_ids(
    embedding_list: List[Tuple[np.ndarray, List[str]]],
    common_ids: List[str],
) -> List[np.ndarray]:
    """Align each embedding array to common IDs."""
    aligned = []

    for embeds, ids in embedding_list:
        aligned_embeds, _ = align_embeddings(
            embeds,
            ids,
            common_ids,
        )
        aligned.append(aligned_embeds)

    return aligned


def fuse_embeddings(
    embedding_list: List[Tuple[np.ndarray, List[str]]],
    target_ids: List[str],
) -> Tuple[np.ndarray, List[str]]:
    """
    Align and concatenate multiple embeddings.
    """
    if not embedding_list:
        return np.array([]), []

    common_ids = find_common_ids(embedding_list, target_ids)

    if not common_ids:
        return np.array([]), []

    aligned = _align_embeddings_to_common_ids(
        embedding_list,
        common_ids,
    )

    fused = np.hstack(aligned)

    return fused, common_ids