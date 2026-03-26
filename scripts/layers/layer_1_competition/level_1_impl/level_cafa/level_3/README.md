# level_cafa level_3

## Purpose

CAFA-specific data preparation for per-ontology training. Uses `OntologyFeatureExtractor` from `level_2` to build feature matrices and binarizes multi-label GO targets from training data.

## Contents

| Module | Description |
|--------|-------------|
| `ontology_data_preparer` | `OntologyDataPreparer` — orchestrates feature extraction and label binarization |

## Public API

Exported via `__init__.py`:

| Symbol | Description |
|--------|-------------|
| OntologyDataPreparer | Prepares features and labels from training data |

## Dependencies

- **level_0** (general): get_logger
- **level_cafa.level_2**: OntologyFeatureExtractor

## Usage Example

```python
from layers.layer_1_competition.level_1_impl.level_cafa.level_3 import OntologyDataPreparer

preparer = OntologyDataPreparer()
X_train, y_train = preparer.prepare_training_data(
    train_data={"sequences": seqs, "terms": terms_df, "protein_ids": ids},
    ontology="F",
    ontology_config={"feature_type": "hand_crafted"},
)
```
