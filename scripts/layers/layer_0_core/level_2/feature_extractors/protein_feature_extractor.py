"""Handcrafted features for protein sequences.

Assembles the full fixed-length feature vector from constituent modules.

Depends on:
    level_0 — AA_ALPHABET, TOP_DIPEPTIDES, TOP_TRIPEPTIDES, HANDCRAFTED_FEATURE_DIM,
              extract_kmer_frequencies
    level_1 — calculate_physicochemical_properties, calculate_ctd_features
"""

import numpy as np

from collections import Counter

from layers.layer_0_core.level_0 import (
    AA_ALPHABET,
    TOP_DIPEPTIDES,
    TOP_TRIPEPTIDES,
    HANDCRAFTED_FEATURE_DIM,
    extract_kmer_frequencies,
)
from layers.layer_0_core.level_1 import (
    calculate_physicochemical_properties,
    calculate_ctd_features,
)

_HYDROPHOBIC_AAS = frozenset('AILMFWYV')
_CHARGED_AAS = frozenset('DEKRH')


def _hydrophobic_fraction(region: str) -> float:
    """Fraction of hydrophobic amino acids in a sequence region."""
    return sum(1 for aa in region if aa in _HYDROPHOBIC_AAS) / len(region)


def _charged_fraction(region: str) -> float:
    """Fraction of charged amino acids in a sequence region."""
    return sum(1 for aa in region if aa in _CHARGED_AAS) / len(region)


def extract_handcrafted_features(seq: str) -> np.ndarray:
    """
    Build a handcrafted feature vector for a single amino acid sequence.

    Feature groups and dimensions:
        AA composition     (20): relative frequency of each standard amino acid.
        Basic properties    (5): log-length, hydrophobicity, charge,
                                 polarity, aromaticity.
        Physicochemical     (8): see calculate_physicochemical_properties.
        CTD features       (17): see calculate_ctd_features.
        Dipeptide freqs    (20): frequency of top-20 fixed dipeptides.
        Tripeptide freqs   (10): frequency of top-10 fixed tripeptides.
        Positional props    (6): hydrophobicity and charge at N/mid/C termini.
        Total: HANDCRAFTED_FEATURE_DIM = 86

    Args:
        seq: Amino acid sequence string.

    Returns:
        Float32 array of HANDCRAFTED_FEATURE_DIM features.
        Zero-filled array if seq is empty.
    """
    if not seq:
        return np.zeros(HANDCRAFTED_FEATURE_DIM, dtype=np.float32)

    aa_counts = Counter(seq)
    length = len(seq)

    # --- AA composition (20 features) ---
    aa_freq = np.array(
        [aa_counts.get(aa, 0) / length for aa in AA_ALPHABET],
        dtype=np.float32,
    )

    # --- Basic properties (5 features) ---
    hydrophobic = sum(aa_counts.get(aa, 0) for aa in _HYDROPHOBIC_AAS) / length
    charged     = sum(aa_counts.get(aa, 0) for aa in _CHARGED_AAS)     / length
    polar       = sum(aa_counts.get(aa, 0) for aa in 'STNQ')           / length
    aromatic    = sum(aa_counts.get(aa, 0) for aa in 'FWY')            / length
    basic_props = np.array(
        [np.log1p(length), hydrophobic, charged, polar, aromatic],
        dtype=np.float32,
    )

    # --- Physicochemical (8 features) ---
    physichem = calculate_physicochemical_properties(seq)

    # --- CTD (17 features) ---
    ctd = calculate_ctd_features(seq)

    # --- Dipeptide frequencies (20 features) ---
    dipeptides = extract_kmer_frequencies(seq, k=2)
    dipeptide_freq = np.array(
        [dipeptides.get(dp, 0.0) for dp in TOP_DIPEPTIDES],
        dtype=np.float32,
    )

    # --- Tripeptide frequencies (10 features) ---
    tripeptides = extract_kmer_frequencies(seq, k=3)
    tripeptide_freq = np.array(
        [tripeptides.get(tp, 0.0) for tp in TOP_TRIPEPTIDES],
        dtype=np.float32,
    )

    # --- Positional properties (6 features) ---
    n_term   = seq[:30]   if length > 30 else seq
    c_term   = seq[-30:]  if length > 30 else seq
    mid_term = seq[30:-30] if length > 60 else None

    positional = np.array([
        _hydrophobic_fraction(n_term),
        _charged_fraction(n_term),
        _hydrophobic_fraction(c_term),
        _charged_fraction(c_term),
        _hydrophobic_fraction(mid_term) if mid_term else hydrophobic,
        _charged_fraction(mid_term)     if mid_term else charged,
    ], dtype=np.float32)

    return np.concatenate([
        aa_freq,         # 20
        basic_props,     #  5
        physichem,       #  8
        ctd,             # 17
        dipeptide_freq,  # 20
        tripeptide_freq, # 10
        positional,      #  6
    ])                   # = 86