# level_cafa (root)

## Purpose

CAFA 6 Protein Function Prediction contest implementation. Aggregates contest-specific configuration, schema, paths, ontology, hierarchy, embedding paths, training utilities, and post-processing. Registers the `cafa` contest with `ContestRegistry` on import.

## Contents

| Sub-package | Description |
|-------------|-------------|
| `level_0` | Configuration, schema, paths, ontology, hierarchy, data loaders, model manager, embedding path resolution, GOA filter, T5 loaders, IA-weighted threshold helpers |
| `level_1` | Embedding loading, post-processing, CAFA parameter grids, training config |
| `level_2` | Feature extraction for per-ontology training |
| `level_3` | Ontology data preparation (features and labels) |
| `level_4` | Per-ontology training orchestration |

## Public API

The root `__init__.py` re-exports the union of `level_0`–`level_4` `__all__` symbols. Common entry points:

| Symbol | Sub-package | Description |
|--------|-------------|-------------|
| CAFAConfig | level_0 | Contest configuration |
| CAFADataSchema | level_0 | Sample ID, target columns, GO validation |
| CAFAPaths | level_0 | Path constants |
| CAFAPostProcessor | level_1 | Hierarchy propagation, GOA filtering, limits |
| CAFAOntologySystem | level_0 | F/P/C (MFO/BPO/CCO) ontology |
| CAFAHierarchy | level_0 | Gene Ontology hierarchy |
| get_embedding_paths | level_0 | Kaggle vs local embedding layout |
| load_embedding_data | level_1 | Load numpy/T5 embeddings |
| OntologyFeatureExtractor | level_2 | Hand-crafted, embedding, or fused features |
| OntologyDataPreparer | level_3 | Features and multi-label targets |
| PerOntologyTrainWorkflow | level_4 | Train per ontology (F, P, C) |

See each level’s README for the full exported list.

## Dependencies

- **`layers.layer_1_competition.level_0_infra.level_0`**: `register_contest` — contest registration on import
- **level_cafa.level_0**: `CAFAConfig`, `CAFADataSchema`, `CAFAPaths`, ontology and loader types
- **level_cafa.level_1**: `CAFAPostProcessor` (registered with the contest in `registration.py`)
- **level_7** (general): `create_tabular_model` — used by `OntologyModelManager` for per-ontology tabular models (see `level_0/README.md`)

### Optional dependencies (T5 / R formats)

Importing `level_cafa` or `level_cafa.level_0` does **not** require these; they load only when you call `load_t5_rds` or `load_t5_qs`:

- **`.rds`**: `pyreadr` (and an R toolchain where `pyreadr` expects it)
- **`.qs`**: `rpy2`, a system **R** install, and the R package **qs**

## Usage Example

```python
from layers.layer_1_competition.level_1_impl import level_cafa  # Triggers register_contest("cafa", ...)

from layers.layer_1_competition.level_1_impl.level_cafa import (
    CAFAConfig,
    CAFADataSchema,
    CAFAPaths,
    CAFAPostProcessor,
    CAFAOntologySystem,
    CAFAHierarchy,
)

config = CAFAConfig(ontology="F")
paths = CAFAPaths()
schema = CAFADataSchema()
ontology = CAFAOntologySystem()
hierarchy = CAFAHierarchy()
post_processor = CAFAPostProcessor(threshold=0.5)
```
