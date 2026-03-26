# level_1/protein

## Purpose
Protein ID normalization (UniProt format) and embedding alignment to common ID sets.

## Contents
- `id_utils.py` — `normalize_protein_id`, `normalize_protein_ids`, `find_common_protein_ids`, `align_embeddings_to_common_ids`

## Public API
- `normalize_protein_id(protein_id)` — Normalize to accession (e.g. sp|Q8VY15|NAME → Q8VY15)
- `normalize_protein_ids(protein_ids)` — Normalize list of IDs
- `find_common_protein_ids(embedding_list, target_ids)` — Intersection with normalization
- `align_embeddings_to_common_ids(embedding_list, common_ids)` — Align embeddings, zero-fill missing

## Dependencies
- `level_0` — `get_logger`

## Usage Example
```python
from level_1.protein import normalize_protein_ids, find_common_protein_ids

normalized = normalize_protein_ids(["sp|Q8VY15|NAME", "P12345"])
common = find_common_protein_ids([(emb1, ids1), (emb2, ids2)], target_ids)
```
