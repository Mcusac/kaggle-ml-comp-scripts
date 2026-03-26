"""Utilities for working with embedding ID sets."""

from typing import List, Tuple

import numpy as np


def find_common_ids(
    embedding_list: List[Tuple[np.ndarray, List[str]]],
    target_ids: List[str],
) -> List[str]:
    """
    Find IDs common to target_ids and every embedding ID list.

    Args:
        embedding_list: List of (embedding_array, id_list) pairs.
        target_ids:     The desired output ID set.

    Returns:
        Sorted list of IDs that appear in target_ids and every id_list.
        Returns empty list if either argument is empty.
    """
    if not embedding_list or not target_ids:
        return []

    common = set(target_ids)
    for _, id_list in embedding_list:
        common &= set(id_list)

    return sorted(common)