# data

## Purpose
Data handling utilities: cross-validation splits, file I/O, image processing pipelines, and domain configuration dataclasses.

## Contents
- `cv_splits/` — K-fold split creation for DataFrames and numpy arrays
- `domain/` — Vision and tabular configuration dataclasses and model components
- `io/` — Generic batch file loading and numpy embedding file loading
- `processing/` — Image preprocessing, augmentation transforms, dataset classes, and transform pipeline composition

## Public API
All sub-package exports are re-exported from this package.

## Dependencies
- `level_0` — `get_logger`, `load_image_pil`, `get_torch`

## Usage Example
```python
from layers.layer_0_core.level_1.data.cv_splits import create_kfold_splits, get_fold_data
from layers.layer_0_core.level_1.data.processing.datasets import BaseImageDataset
df_with_folds = create_kfold_splits(df, n_folds=5)
```