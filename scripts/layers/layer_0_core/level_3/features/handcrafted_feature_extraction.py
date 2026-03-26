"""Handcrafted feature extraction: sequential batch, parallel batch, and memory-safe streaming."""

import os
import numpy as np

from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Generator, List, Optional, Tuple

from level_0 import get_logger, HANDCRAFTED_FEATURE_DIM
from level_2 import extract_handcrafted_features

logger = get_logger(__name__)

_DEFAULT_CHUNK_SIZE: int = 10_000


# ---------------------------------------------------------------------------
# Private core
# ---------------------------------------------------------------------------

def _extract_one(pid: str, sequences: Dict[str, str]) -> np.ndarray:
    """
    Extract features for a single protein ID.

    Returns the feature vector from extract_handcrafted_features when the ID
    is present, or a zero-filled float32 vector when it is absent.

    Args:
        pid: Protein identifier.
        sequences: Mapping of protein_id -> amino acid sequence.

    Returns:
        Float32 array of shape (HANDCRAFTED_FEATURE_DIM,).
    """
    seq = sequences.get(pid)
    if seq:
        return extract_handcrafted_features(seq)
    return np.zeros(HANDCRAFTED_FEATURE_DIM, dtype=np.float32)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_handcrafted_features_for_ids(
    sequences: Dict[str, str],
    protein_ids: List[str],
) -> np.ndarray:
    """
    Extract handcrafted features for an ordered list of protein IDs sequentially.

    Proteins absent from sequences receive a zero-filled feature vector.
    For thread-based parallelism over large lists use extract_handcrafted_parallel.

    Args:
        sequences: Mapping of protein_id -> amino acid sequence.
        protein_ids: Ordered list of IDs to process. Output row order matches
                     this list exactly.

    Returns:
        Float32 array of shape (len(protein_ids), HANDCRAFTED_FEATURE_DIM).
    """
    rows = [_extract_one(pid, sequences) for pid in protein_ids]
    return np.array(rows, dtype=np.float32)


def extract_handcrafted_parallel(
    sequences: Dict[str, str],
    protein_ids: List[str],
    max_workers: Optional[int] = None,
) -> np.ndarray:
    """
    Extract handcrafted features for a list of protein IDs using a thread pool.

    Proteins absent from sequences receive a zero-filled feature vector.
    Thread-based parallelism is appropriate because the GIL is released during
    the numpy operations inside extract_handcrafted_features.

    Args:
        sequences: Mapping of protein_id -> amino acid sequence.
        protein_ids: Ordered list of IDs to process. Output row order matches
                     this list exactly.
        max_workers: Thread pool size. Defaults to min(4, os.cpu_count()).

    Returns:
        Float32 array of shape (len(protein_ids), HANDCRAFTED_FEATURE_DIM).
    """
    if max_workers is None:
        max_workers = min(4, os.cpu_count() or 1)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        rows = list(executor.map(lambda pid: _extract_one(pid, sequences), protein_ids))

    result = np.array(rows, dtype=np.float32)
    logger.info(f"Extracted features for {len(protein_ids):,} proteins: shape {result.shape}")
    return result


def stream_features(
    sequences: Dict[str, str],
    chunk_size: Optional[int] = None,
) -> Generator[Tuple[np.ndarray, List[str]], None, None]:
    """
    Yield handcrafted features in chunks for memory-efficient processing.

    Avoids holding all feature vectors in memory simultaneously. Each chunk
    is extracted sequentially via extract_handcrafted_features_for_ids.

    Args:
        sequences: Mapping of protein_id -> amino acid sequence.
        chunk_size: Number of proteins per chunk (default: 10_000).

    Yields:
        (feature_matrix, protein_ids) for each chunk, where feature_matrix is
        a float32 array of shape (chunk_size, HANDCRAFTED_FEATURE_DIM).
    """
    if chunk_size is None:
        chunk_size = _DEFAULT_CHUNK_SIZE

    protein_ids = list(sequences.keys())
    total = len(protein_ids)
    logger.info(f"Streaming features for {total:,} proteins in chunks of {chunk_size:,}")

    for chunk_num, start in enumerate(range(0, total, chunk_size), start=1):
        chunk_ids = protein_ids[start:start + chunk_size]
        features = extract_handcrafted_features_for_ids(sequences, chunk_ids)
        logger.info(f"  Chunk {chunk_num}: {len(chunk_ids):,} proteins, shape {features.shape}")
        yield features, chunk_ids

    logger.info(f"Streamed all {total:,} proteins")