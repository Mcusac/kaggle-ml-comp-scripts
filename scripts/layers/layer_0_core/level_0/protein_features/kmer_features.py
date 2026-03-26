"""K-mer frequency feature extraction from sequences.

No dependencies on other protein_features modules.
Operates on raw string sequences only.
"""

from collections import Counter
from typing import Dict


def extract_kmer_frequencies(seq: str, k: int = 2) -> Dict[str, float]:
    """
    Compute relative k-mer frequencies from a sequence.

    Args:
        seq: Input sequence string.
        k: K-mer length (default 2 for dipeptides).

    Returns:
        Dict mapping each observed k-mer to its relative frequency in [0, 1].
        Returns empty dict if seq is shorter than k or empty.

    Example:
        >>> extract_kmer_frequencies("ACAC", k=2)
        {'AC': 0.6667, 'CA': 0.3333}
    """
    if not seq or len(seq) < k:
        return {}

    kmers = [seq[i:i + k] for i in range(len(seq) - k + 1)]
    counts = Counter(kmers)
    total = len(kmers)

    return {kmer: count / total for kmer, count in counts.items()}