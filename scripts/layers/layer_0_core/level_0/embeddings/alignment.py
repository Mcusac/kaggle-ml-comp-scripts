"""Embedding alignment utilities."""

import numpy as np

from typing import List, Tuple


def align_embeddings(
    embeds: np.ndarray,
    embed_ids: List[str],
    target_ids: List[str],
) -> Tuple[np.ndarray, List[str]]:
    """
    Align embeddings to target IDs, filling missing IDs with zero vectors.
    """
    if len(embeds) == 0:
        raise ValueError("embeds is empty; cannot infer feature dimension")

    embed_dict = {pid: emb for pid, emb in zip(embed_ids, embeds)}

    feat_dim = embeds.shape[1]
    aligned = []

    for pid in target_ids:
        if pid in embed_dict:
            aligned.append(embed_dict[pid])
        else:
            aligned.append(np.zeros(feat_dim, dtype=np.float32))

    return np.array(aligned), target_ids