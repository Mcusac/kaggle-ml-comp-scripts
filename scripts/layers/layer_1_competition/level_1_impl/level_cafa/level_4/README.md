# level_cafa level_4

## Purpose

Per-ontology training workflow for CAFA 6. Trains separate models for each ontology (F, P, C) with ontology-specific hyperparameters, supporting sequential training with GPU cleanup and parallel training.

## Contents

| Module | Description |
|--------|-------------|
| `per_ontology_training` | PerOntologyTrainWorkflow: orchestrates data loading, preparation, model creation, training, and saving per ontology |

## Public API

Exported via `__init__.py`:

| Symbol | Description |
|--------|-------------|
| PerOntologyTrainWorkflow | Workflow for training models per ontology with separate hyperparameters |

## Dependencies

- **level_0** (general): get_logger
- **level_1** (general): cleanup_gpu_memory, OntologyConfigResolver
- **level_cafa level_0**: CAFA_ONTOLOGIES, OntologyDataLoader, OntologyModelManager
- **level_cafa level_3**: OntologyDataPreparer

## Usage Example

```python
from layers.layer_1_competition.level_1_impl.level_cafa.level_4 import PerOntologyTrainWorkflow

workflow = PerOntologyTrainWorkflow(config=train_config, contest=cafa_contest)
results = workflow.run_train_all(sequential=True)
```
