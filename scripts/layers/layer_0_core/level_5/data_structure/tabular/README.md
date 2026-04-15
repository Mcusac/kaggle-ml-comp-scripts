# data_structure.tabular

## Purpose

Base classes for tabular models and sparse multi-label datasets.

## Contents

- **base.py**: BaseTabularModel (abstract)
- **sparse_tabular_dataset.py**: SparseTabularDataset

## Public API

- `BaseTabularModel` — Abstract base with fit, predict, predict_proba, save, load, get_params, set_params
- `SparseTabularDataset` — PyTorch Dataset for sparse labels with memmap features and label smoothing

## Dependencies

- level_0: get_logger, ensure_file_dir, get_torch
- level_4: load_json, save_pickle, load_pickle

## Usage Example

```python
from layers.layer_0_core.level_5 import BaseTabularModel, SparseTabularDataset
import numpy as np
from scipy.sparse import csr_matrix

class MyModel(BaseTabularModel):
    def fit(self, X, y, **kwargs): ...
    def predict_proba(self, X): ...
    def save(self, path): ...
    def load(self, path): ...

ds = SparseTabularDataset(X, y_sparse, label_smoothing=0.1)
```
