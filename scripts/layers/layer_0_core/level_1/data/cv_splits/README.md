# data/cv_splits

## Purpose
K-fold cross-validation split assignment for both DataFrame rows and numpy feature arrays.

## Contents
- `arrays.py` — `split_features_by_fold`: splits numpy feature/target arrays by fold index
- `dataframes.py` — `create_kfold_splits`: assigns fold column to a DataFrame; `get_fold_data`: filters by fold

## Public API
- `split_features_by_fold(all_features, all_targets, fold_assignments, current_fold)` — returns train/val array splits
- `create_kfold_splits(data, n_folds, shuffle, random_state, stratify)` — adds `fold` column to DataFrame
- `get_fold_data(data, fold, train)` — filters DataFrame to training or validation rows for a given fold

## Dependencies
- `level_0` — `get_logger`
- `sklearn.model_selection` — `KFold`, `StratifiedKFold`

## Usage Example
```python
from level_1.data.cv_splits import create_kfold_splits, get_fold_data
df = create_kfold_splits(df, n_folds=5)
train_df = get_fold_data(df, fold=0, train=True)
val_df = get_fold_data(df, fold=0, train=False)
```