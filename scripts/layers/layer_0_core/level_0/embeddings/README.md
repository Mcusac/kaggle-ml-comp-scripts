# Embeddings

Embedding alignment and ID set utilities.

## Purpose

Provides utilities for aligning embedding arrays to a target ID list and for computing ID intersections between embedding sets.

## Contents

- `alignment.py` – `align_embeddings`: align an embedding matrix to a target ID list, filling missing IDs with zero vectors
- `id_ops.py` – `find_common_ids`: compute the intersection of IDs across multiple embedding sets
- `normalize.py` – `normalize_embedding_type`: resolve embedding type via optional alias mapping
- `path_resolver.py` – `resolve_embedding_base_path`: resolve base path for an embedding type

## Public API

- `align_embeddings(embeds, embed_ids, target_ids)` – Align embeddings to target IDs; raises `ValueError` if `embeds` is empty
- `find_common_ids(embedding_list, target_ids)` – Return the sorted list of IDs common to target_ids and every embedding ID list
- `normalize_embedding_type(embedding_type, aliases)` – Resolve embedding type using optional alias dict
- `resolve_embedding_base_path(embedding_type, base_path, paths_config)` – Resolve base path for embedding type

## Dependencies

- numpy

## Usage Example

```python
import numpy as np
from layers.layer_0_core.level_0 import align_embeddings, find_common_ids

embeds = np.random.rand(3, 128).astype(np.float32)
ids = ["a", "b", "c"]
target = ["b", "c", "d"]

aligned, aligned_ids = align_embeddings(embeds, ids, target)
# aligned.shape == (3, 128); row for "d" is zeros
```
