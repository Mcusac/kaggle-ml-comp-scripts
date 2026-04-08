"""Split helpers for contest training data."""

from typing import Optional, Tuple

import pandas as pd
from sklearn.model_selection import train_test_split

from layers.layer_0_core.level_1 import create_kfold_splits, get_fold_data


def split_train_val(
    *,
    train_data: pd.DataFrame,
    validation_split: Optional[float],
    n_folds: Optional[int],
    fold: Optional[int],
) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
    val_data = None
    if n_folds is not None and n_folds > 1:
        train_data = create_kfold_splits(train_data, n_folds=n_folds, shuffle=True, random_state=42)
        if fold is not None:
            val_data = get_fold_data(train_data, fold=fold, train=False)
            train_data = get_fold_data(train_data, fold=fold, train=True)
    elif validation_split is not None and 0 < validation_split < 1:
        train_data, val_data = train_test_split(train_data, test_size=validation_split, random_state=42)
    return train_data, val_data

