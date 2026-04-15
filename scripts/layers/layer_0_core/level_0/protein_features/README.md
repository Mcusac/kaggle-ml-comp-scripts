# Protein Features

Amino acid constants and k-mer frequency feature extraction.

## Purpose

Provides physicochemical constants for amino acids and utilities for computing k-mer frequency features from protein sequences.

## Contents

- `amino_acid_constants.py` – Physicochemical lookup tables and sequence alphabet constants
- `kmer_features.py` – `extract_kmer_frequencies`: compute k-mer frequency vectors from a sequence

## Public API

- `AA_WEIGHTS` – Monoisotopic molecular weights per amino acid
- `HYDROPATHY_VALUES` – Kyte-Doolittle hydropathy index per amino acid
- `AA_ALPHABET` – Canonical 20-letter amino acid alphabet string
- `AA_GROUPS` – Grouping of amino acids by physicochemical property
- `TOP_DIPEPTIDES` – Most frequent dipeptides used as feature basis
- `TOP_TRIPEPTIDES` – Most frequent tripeptides used as feature basis
- `HANDCRAFTED_FEATURE_DIM` – Total dimension of handcrafted feature vector
- `extract_kmer_frequencies(sequence, k)` – Return a frequency vector over the k-mer vocabulary

## Dependencies

- stdlib: typing
- numpy

## Usage Example

```python
from layers.layer_0_core.level_0 import extract_kmer_frequencies, AA_ALPHABET

freqs = extract_kmer_frequencies("ACDEFGHIKLM", k=2)
```
