"""Amino acid physicochemical constants and classification groupings.

No project-level dependencies. Pure data definitions.
"""

from typing import Dict, Set

# Molecular weights (Daltons) for the 20 standard amino acids
AA_WEIGHTS: Dict[str, float] = {
    'A':  89.1, 'C': 121.2, 'D': 133.1, 'E': 147.1, 'F': 165.2,
    'G':  75.1, 'H': 155.2, 'I': 131.2, 'K': 146.2, 'L': 131.2,
    'M': 149.2, 'N': 132.1, 'P': 115.1, 'Q': 146.2, 'R': 174.2,
    'S': 105.1, 'T': 119.1, 'V': 117.1, 'W': 204.2, 'Y': 181.2,
}

# Kyte-Doolittle hydropathy index
HYDROPATHY_VALUES: Dict[str, float] = {
    'A':  1.8, 'C':  2.5, 'D': -3.5, 'E': -3.5, 'F':  2.8,
    'G': -0.4, 'H': -3.2, 'I':  4.5, 'K': -3.9, 'L':  3.8,
    'M':  1.9, 'N': -3.5, 'P': -1.6, 'Q': -3.5, 'R': -4.5,
    'S': -0.8, 'T': -0.7, 'V':  4.2, 'W': -0.9, 'Y': -1.3,
}

# Canonical ordering of the 20 standard amino acids (for composition vectors)
AA_ALPHABET: str = 'ACDEFGHIKLMNPQRSTVWY'

# Groupings used for CTD (Composition-Transition-Distribution) features
AA_GROUPS: Dict[str, Set[str]] = {
    'hydrophobic':   set('AILMFWYV'),
    'polar':         set('RKHDESTQNC'),
    'positive':      set('RKH'),
    'negative':      set('DE'),
    'neutral_polar': set('STNQ'),
    'aromatic':      set('FWY'),
    'aliphatic':     set('ILV'),
    'small':         set('ACDGNPSTV'),
}

# Fixed k-mer vocabularies for dipeptide/tripeptide features.
# These represent the most common patterns across protein databases.
TOP_DIPEPTIDES = [
    'AL', 'LA', 'LE', 'EA', 'AA', 'AS', 'SA', 'EL', 'LL', 'AE',
    'SE', 'ES', 'GA', 'AG', 'VA', 'AV', 'LV', 'VL', 'LS', 'SL',
]
TOP_TRIPEPTIDES = [
    'ALA', 'LEA', 'EAL', 'LAL', 'AAA', 'LLE', 'ELE', 'ALE', 'GAL', 'ASA',
]

# Total feature dimension produced by extract_handcrafted_features.
# Breakdown: AA composition (20) + basic props (5) + physicochemical (8)
#          + CTD (17) + dipeptides (20) + tripeptides (10) + positional (6) = 86
#
# NOTE: The original file documented 90 features with 21 CTD features.
# The actual CTD implementation produces 17 (8 composition + 3 transition + 6 distribution).
# HANDCRAFTED_FEATURE_DIM is 86 to match what the code actually produces.
# If the CTD implementation is corrected to produce 21 features, update this to 90.
HANDCRAFTED_FEATURE_DIM: int = 86