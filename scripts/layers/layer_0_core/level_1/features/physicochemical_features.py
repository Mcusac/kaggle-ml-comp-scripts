"""Physicochemical and CTD feature extraction for amino acid sequences.

Depends on: amino_acid_constants (for AA_WEIGHTS, HYDROPATHY_VALUES, AA_GROUPS)
"""

from collections import Counter

import numpy as np

from layers.layer_0_core.level_0 import (
    AA_GROUPS, AA_WEIGHTS, HYDROPATHY_VALUES
)

def calculate_physicochemical_properties(seq: str) -> np.ndarray:
    """
    Compute 8 physicochemical properties from an amino acid sequence.

    Properties (in order):
        1. log(molecular weight)  — log1p of summed residue weights
        2. Aliphatic index        — weighted fraction of A, V, I, L
        3. Instability index      — simplified fraction of DEKRH residues × 100
        4. Positive fraction      — fraction of RKH residues
        5. Negative fraction      — fraction of DE residues
        6. Net charge             — positive minus negative fractions
        7. GRAVY score            — mean Kyte-Doolittle hydropathy
        8. Aromaticity            — fraction of FWY residues

    Args:
        seq: Amino acid sequence string.

    Returns:
        Float32 array of 8 values. Zero array if seq is empty.
    """
    if not seq:
        return np.zeros(8, dtype=np.float32)

    aa_counts = Counter(seq)
    length = len(seq)

    mol_weight = sum(
        count * AA_WEIGHTS.get(aa, 0.0) for aa, count in aa_counts.items()
    )
    aliphatic = (
        aa_counts.get('A', 0)
        + 2.9 * aa_counts.get('V', 0)
        + 3.9 * (aa_counts.get('I', 0) + aa_counts.get('L', 0))
    ) / length
    instability = sum(aa_counts.get(aa, 0) for aa in 'DEKRH') / length * 100
    positive    = sum(aa_counts.get(aa, 0) for aa in 'RKH') / length
    negative    = sum(aa_counts.get(aa, 0) for aa in 'DE') / length
    net_charge  = positive - negative
    gravy = sum(
        count * HYDROPATHY_VALUES.get(aa, 0.0) for aa, count in aa_counts.items()
    ) / length
    aromaticity = sum(aa_counts.get(aa, 0) for aa in 'FWY') / length

    return np.array(
        [np.log1p(mol_weight), aliphatic, instability,
         positive, negative, net_charge, gravy, aromaticity],
        dtype=np.float32,
    )


def calculate_ctd_features(seq: str) -> np.ndarray:
    """
    Compute Composition-Transition-Distribution (CTD) features.

    Feature layout (17 total):
        Composition (8):    fraction of residues in each of the 8 AA_GROUPS.
        Transition  (3):    fraction of adjacent-residue group changes,
                            computed for the first 3 AA_GROUPS.
        Distribution (6):  normalised first / middle / last occurrence positions,
                            computed for the first 2 AA_GROUPS (3 positions each).

    NOTE: The original monolithic file documented 21 CTD features.
    The actual implementation produces 17 (8 + 3 + 6). This is the correct
    value; HANDCRAFTED_FEATURE_DIM in amino_acid_constants reflects this.

    Args:
        seq: Amino acid sequence string.

    Returns:
        Float32 array of 17 CTD values. Zero array if seq is empty.
    """
    if not seq:
        return np.zeros(17, dtype=np.float32)

    group_list = list(AA_GROUPS.values())
    features: list = []

    # Composition — 8 features, one per group
    for group_aas in group_list:
        features.append(sum(1 for aa in seq if aa in group_aas) / len(seq))

    # Transition — 3 features, first 3 groups
    for group_aas in group_list[:3]:
        transitions = sum(
            1 for i in range(len(seq) - 1)
            if (seq[i] in group_aas) != (seq[i + 1] in group_aas)
        )
        features.append(transitions / (len(seq) - 1) if len(seq) > 1 else 0.0)

    # Distribution — 6 features, first 2 groups × 3 positions
    for group_aas in group_list[:2]:
        positions = [i for i, aa in enumerate(seq) if aa in group_aas]
        if positions:
            features.extend([
                positions[0] / len(seq),
                positions[len(positions) // 2] / len(seq),
                positions[-1] / len(seq),
            ])
        else:
            features.extend([0.0, 0.0, 0.0])

    return np.array(features, dtype=np.float32)