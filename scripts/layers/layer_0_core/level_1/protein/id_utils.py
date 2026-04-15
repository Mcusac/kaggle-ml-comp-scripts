"""Protein ID normalization and embedding alignment utilities."""

import numpy as np
from typing import List, Tuple, Union

from layers.layer_0_core.level_0 import get_logger

logger = get_logger(__name__)


def normalize_protein_id(protein_id: Union[str, int, float]) -> str:
    """
    Normalize protein ID to standard format.

    Handles UniProt format: sp|Q8VY15|NAME -> Q8VY15

    Args:
        protein_id: Protein ID in various formats

    Returns:
        Normalized protein ID (accession as string)
    """
    if not protein_id:
        return str(protein_id) if protein_id is not None else ""
    protein_id = str(protein_id)
    if "|" in protein_id:
        parts = protein_id.split("|")
        if len(parts) >= 2:
            return parts[1]
    return protein_id


def normalize_protein_ids(protein_ids: List[Union[str, int, float]]) -> List[str]:
    """Normalize a list of protein IDs."""
    return [normalize_protein_id(pid) for pid in protein_ids]


def find_common_protein_ids(
    embedding_list: List[Tuple[np.ndarray, List[str]]],
    target_ids: List[str],
) -> List[str]:
    """
    Find common protein IDs across embeddings and target IDs.

    Args:
        embedding_list: List of (embedding_array, id_list) tuples
        target_ids: Target protein IDs to align to

    Returns:
        List of common protein IDs (normalized), preserving target order
    """
    id_sets = []
    for _, embed_ids in embedding_list:
        normalized_ids = {normalize_protein_id(str(pid)) for pid in embed_ids}
        id_sets.append(normalized_ids)

    if id_sets:
        embedding_intersection = (
            set.intersection(*id_sets) if len(id_sets) > 1 else id_sets[0]
        )
        logger.debug(
            f"Intersection of {len(id_sets)} embedding types: "
            f"{len(embedding_intersection):,} proteins"
        )
        target_id_set = {normalize_protein_id(str(pid)) for pid in target_ids}
        logger.debug(f"Target IDs: {len(target_id_set):,} proteins")
        all_id_sets = id_sets + [target_id_set]
        common_id_set = set.intersection(*all_id_sets)
        normalized_target_ids = [normalize_protein_id(str(pid)) for pid in target_ids]
        common_ids = [pid for pid in normalized_target_ids if pid in common_id_set]
        logger.info(
            f"Found {len(common_ids):,} common proteins across {len(id_sets)} "
            f"embedding types and {len(target_ids):,} target IDs"
        )
        if len(common_ids) == 0:
            logger.warning("No common IDs found across embeddings and target_ids")
            if len(embedding_intersection) > 0:
                overlap = embedding_intersection & target_id_set
                logger.warning(
                    f"Overlap between embedding IDs and target IDs: {len(overlap):,} proteins"
                )
        return common_ids

    return [normalize_protein_id(str(pid)) for pid in target_ids]


def align_embeddings_to_common_ids(
    embedding_list: List[Tuple[np.ndarray, List[str]]],
    common_ids: List[str],
) -> List[np.ndarray]:
    """
    Align each embedding array to common protein IDs.

    Missing proteins get zero vectors.

    Args:
        embedding_list: List of (embedding_array, id_list) tuples
        common_ids: Common protein IDs to align to

    Returns:
        List of aligned embedding arrays
    """
    aligned_embeddings = []
    for embeds, embed_ids in embedding_list:
        normalized_embed_ids = [normalize_protein_id(str(pid)) for pid in embed_ids]
        embed_dict = dict(zip(normalized_embed_ids, embeds))
        aligned = []
        for norm_pid in common_ids:
            if norm_pid in embed_dict:
                aligned.append(embed_dict[norm_pid])
            else:
                aligned.append(np.zeros(embeds.shape[1], dtype=embeds.dtype))
        aligned_embeddings.append(np.array(aligned))
    return aligned_embeddings
