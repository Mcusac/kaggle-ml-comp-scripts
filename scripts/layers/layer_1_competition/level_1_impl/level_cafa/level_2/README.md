# level_cafa level_2

## Purpose

CAFA-specific feature extraction for per-ontology training. Builds hand-crafted, embedding-only, or fused feature matrices using generic feature utilities and CAFA embedding loading from `level_1`.

## Contents

| Module | Description |
|--------|-------------|
| `feature_extractor` | `OntologyFeatureExtractor` — hand-crafted, embedding, or fused features |

## Public API

Exported via `__init__.py`:

| Symbol | Description |
|--------|-------------|
| OntologyFeatureExtractor | Extracts protein features for ontology training |

## Dependencies

- **level_0** (general): get_logger, align_embeddings, HANDCRAFTED_FEATURE_DIM
- **level_1** (general): fuse_embeddings
- **level_2** (general): extract_handcrafted_features
- **level_cafa.level_1**: load_embedding_data

## Usage Example

```python
from layers.layer_1_competition.level_1_impl.level_cafa.level_2 import OntologyFeatureExtractor

extractor = OntologyFeatureExtractor()
features = extractor.extract_features(
    train_seqs=seq_dict,
    protein_ids=ids,
    feature_type="embeddings",
    ontology_config={"embedding_type": "esm2_650m"},
)
```
