# level_1

## Purpose
Framework utilities for ML pipelines. Provides reusable building blocks for data handling, training, evaluation, feature extraction, hyperparameter search, and runtime infrastructure. Depends only on `level_0`.

## Contents
- `cli/` — Framework CLI subparsers and command builders (train, grid search, ensemble, etc.)
- `data/` — CV split generation, batch I/O, image preprocessing, augmentation, datasets, and domain config
- `evaluation/` — Custom loss functions, metric registry, and fold analysis
- `features/` — Feature extraction base, cache I/O, filename codec, registry, and optional SigLIP accessors
- `grid_search/` — Pareto frontier utilities for multi-objective search results
- `guards/` — Pure invariant guards that raise on violation
- `io/` — TSV submission formatting
- `ontology/` — OBO parsing helpers and hierarchy propagation for structured labels
- `pipelines/` — Pipeline orchestration and shells
- `protein/` — Protein ID normalization helpers
- `runtime/` — Hardware detection, environment paths, subprocess execution, reproducibility, GPU memory, and progress config
- `search/` — Hyperparameter grid profiles and variant generation/execution primitives
- `training/` — Checkpoint I/O, training loop primitives, and mixed precision setup

## Public API
All symbols exported via sub-package `__init__.py` files. Import from `level_1` directly or from the relevant sub-package.

## Dependencies
- `level_0` — logging, device access, config extraction, error types, path utilities, grid search combinatorics

## Usage Example
```python
import path_bootstrap

path_bootstrap.prepend_framework_paths()

from layers.layer_0_core.level_1 import (
    FocalLoss,
    create_kfold_splits,
    save_checkpoint,
    train_one_epoch,
)
```