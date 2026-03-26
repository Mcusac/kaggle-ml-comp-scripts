# level_cafa level_1

## Purpose

CAFA-specific embedding I/O, post-processing, hyperparameter grids, and training configuration. Loads embeddings using `level_0` path resolution; applies hierarchy propagation and GOA filtering via `CAFAPostProcessor`; resolves per-ontology parameter grids and `CAFATrainingConfig`.

## Contents

| Module | Description |
|--------|-------------|
| `load_embeddings` | `load_embedding_data` — numpy and T5 embeddings using CAFA paths |
| `post_processor` | `CAFAPostProcessor` — hierarchy propagation, GOA filtering, prediction limits |
| `parameter_grids` | `resolve_cafa_param_grid`, `get_ontology_param_grid`, `get_default_param_grid` |
| `training` | `CAFATrainingConfig` — per-ontology hyperparameter overrides |

## Public API

Exported via `__init__.py`:

| Symbol | Description |
|--------|-------------|
| CAFAPostProcessor | Post-processor with hierarchy propagation, GOA filtering, limit enforcement |
| CAFATrainingConfig | Multitask-style config with per-ontology hyperparameter overrides |
| get_default_param_grid | Default parameter grid from config |
| get_ontology_param_grid | Per-ontology grid when present, else default |
| load_embedding_data | Load embeddings for `embedding_type` and `datatype` |
| resolve_cafa_param_grid | Resolve keyed grid for optional ontology and quick mode |

## Dependencies

- **level_0** (general): get_logger; `load_ids_file`, `build_embedding_error_message`, `load_embeddings_file`
- **level_2** (general): `MultiTaskTrainingConfig`, `resolve_keyed_param_grid`
- **layers.layer_1_competition.level_0_infra.level_0**: `ContestPostProcessor` (post-processor base)
- **level_cafa.level_0**: embedding path helpers, T5 loaders, `GOAFilter`

## Usage Example

```python
from layers.layer_1_competition.level_1_impl.level_cafa.level_1 import (
    load_embedding_data,
    CAFAPostProcessor,
    resolve_cafa_param_grid,
    CAFATrainingConfig,
)

embeddings, ids = load_embedding_data("esm2_650m", datatype="train")

processor = CAFAPostProcessor(threshold=0.5)
processor.set_hierarchy(parents_map, term_to_idx)
processed = processor.apply(predictions)

grid = resolve_cafa_param_grid(config.param_grids, ontology="F", quick_mode=False)
train_cfg = CAFATrainingConfig(per_ontology_hyperparams={"F": {"learning_rate": 1e-3}})
```
