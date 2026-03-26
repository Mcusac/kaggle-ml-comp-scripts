# level_cafa level_0

## Purpose

CAFA 6 protein function prediction base layer. Provides configuration, schema, paths, ontology system, hierarchy, data loaders, model manager, CAFA embedding path resolution, GOA filtering utilities, T5 embedding loaders, and IA-weighted threshold optimization.

## Contents

| Module | Description |
|--------|-------------|
| `config` | `CAFAConfig` — contest configuration with ontology support |
| `constants` | `CAFA_ONTOLOGIES`, `validate_ontology` |
| `data_schema` | `CAFADataSchema` — sample ID, target columns, GO term validation |
| `embedding_paths` | Kaggle vs local paths; `get_embedding_paths`, `resolve_base_path`, `resolve_embedding_paths`, `normalize_embedding_type_cafa` |
| `goa_filter` | `GOAFilter` — GOA negative annotation propagation for submissions |
| `hierarchy` | `CAFAHierarchy` — Gene Ontology hierarchy and propagation |
| `ontology` | `CAFAOntologySystem` — F/P/C (MFO/BPO/CCO) ontology definitions |
| `ontology_data_loader` | `OntologyDataLoader` — per-ontology training data loading |
| `ontology_model_manager` | `OntologyModelManager` — model creation, training, saving |
| `paths` | `CAFAPaths` — Kaggle dataset and local path constants |
| `threshold_optimization` | `optimize_threshold_ia_weighted`, `load_ia_weights` — IA-weighted F1 |
| `t5_loader` | `load_t5_rds`, `load_t5_qs` — T5 embeddings from R formats (optional `pyreadr` / `rpy2`+R only when these functions run; not required to import the package) |

## Public API

Exported via `__init__.py` (see `__all__` for the canonical alphabetical list):

| Symbol | Description |
|--------|-------------|
| CAFAConfig | CAFA contest configuration |
| CAFADataSchema | CAFA data schema |
| CAFAHierarchy | GO hierarchy with propagation |
| CAFAOntologySystem | Ontology system for F/P/C |
| CAFA_ONTOLOGIES | Tuple of ontology codes ('F', 'P', 'C') |
| CAFAPaths | CAFA path constants |
| GOAFilter | GOA negative annotation filtering |
| OntologyDataLoader | Per-ontology training data loader |
| OntologyModelManager | Model creation, training, saving |
| get_embedding_paths | `(embedding_paths dict, cafa6_embeddings_dir)` for Kaggle or local |
| load_ia_weights | Load IA weights from IA.tsv |
| load_t5_qs / load_t5_rds | Load T5 embeddings from .qs / .rds |
| normalize_embedding_type_cafa | Normalize embedding type (e.g. esm2 → esm2_650m) |
| optimize_threshold_ia_weighted | Grid search for best IA-weighted F1 threshold |
| resolve_base_path / resolve_embedding_paths | Resolve embedding file paths |
| validate_ontology | Validate F/P/C ontology code |

## Dependencies

- **level_0** (general): get_logger, normalize_embedding_type, resolve_embedding_base_path (via `embedding_paths`)
- **level_1** (general): `HierarchyPropagator` (via `goa_filter`)
- **level_7** (general): `create_tabular_model` (via `ontology_model_manager`)
- **`layers.layer_1_competition.level_0_infra.level_0.abstractions`**: `ContestConfig`, `ContestPaths`, `ContestDataSchema`, `ContestOntologySystem`, `ContestHierarchy` (protocols / shared types)
- **layers.layer_1_competition.level_0_infra.level_0**: `is_kaggle_input` (via `embedding_paths`)

## Usage Example

```python
from layers.layer_1_competition.level_1_impl.level_cafa.level_0 import (
    CAFAConfig,
    CAFAPaths,
    CAFAOntologySystem,
    CAFAHierarchy,
    OntologyDataLoader,
    get_embedding_paths,
    load_t5_rds,
)

config = CAFAConfig(ontology='F')
paths = CAFAPaths()
ontology_system = CAFAOntologySystem()
hierarchy = CAFAHierarchy()
loader = OntologyDataLoader()

embedding_paths, cafa6_dir = get_embedding_paths()

# Load T5 embeddings
embeds, ids = load_t5_rds(paths.get_data_root() / 'Train' / 'train_embeddings.rds', 'train', use_memmap=False)
```
