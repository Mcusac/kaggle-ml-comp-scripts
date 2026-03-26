# level_1

## Purpose
Framework utilities for ML pipelines. Provides reusable building blocks for data handling, training, evaluation, feature extraction, hyperparameter search, and runtime infrastructure. Depends only on `level_0`.

## Contents
- `data/` — CV split generation, batch I/O, image preprocessing, augmentation, datasets, and domain config
- `evaluation/` — Custom loss functions, metric registry, and fold analysis
- `features/` — Feature extraction base, cache I/O, filename codec, registry, and optional SigLIP accessors
- `guards/` — Pure invariant guards that raise on violation
- `runtime/` — Hardware detection, environment paths, subprocess execution, reproducibility, GPU memory, CLI builders, and progress config
- `search/` — Hyperparameter grid profiles and variant generation/execution primitives
- `training/` — Checkpoint I/O, optimizer/scheduler/loss factories, training loop primitives, and mixed precision setup

## Public API
All symbols exported via sub-package `__init__.py` files. Import from `level_1` directly or from the relevant sub-package.

## Dependencies
- `level_0` — logging, device access, config extraction, error types, path utilities, grid search combinatorics

## Usage Example
```python
from level_1.data.cv_splits import create_kfold_splits
from level_1.training import save_checkpoint, train_one_epoch
from level_1.evaluation import FocalLoss
```