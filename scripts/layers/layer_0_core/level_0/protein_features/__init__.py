"""Protein features utilities."""

from .amino_acid_constants import (
    AA_WEIGHTS, HYDROPATHY_VALUES,
    AA_ALPHABET, AA_GROUPS,
    TOP_DIPEPTIDES, TOP_TRIPEPTIDES,
    HANDCRAFTED_FEATURE_DIM,
)
from .kmer_features import extract_kmer_frequencies

__all__ = [
    "AA_WEIGHTS",
    "HYDROPATHY_VALUES",
    "AA_ALPHABET",
    "AA_GROUPS",
    "TOP_DIPEPTIDES",
    "TOP_TRIPEPTIDES",
    "HANDCRAFTED_FEATURE_DIM",
    "extract_kmer_frequencies",
]