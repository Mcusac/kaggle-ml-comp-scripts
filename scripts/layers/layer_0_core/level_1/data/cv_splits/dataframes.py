"""Cross-validation split logic for DataFrames."""

import pandas as pd

from sklearn.model_selection import KFold, StratifiedKFold
from typing import Optional

from level_0 import get_logger

logger = get_logger(__name__)


def create_kfold_splits(
    data: pd.DataFrame,
    n_folds: int = 5,
    shuffle: bool = True,
    random_state: int = 42,
    stratify: Optional[str] = None
) -> pd.DataFrame:
    """
    Create K-fold cross-validation splits.

    Args:
        data: DataFrame with aggregated data (1 row per image). Must not be empty.
        n_folds: Number of folds (default: 5). Must be >= 2.
        shuffle: Whether to shuffle data before splitting (default: True).
        random_state: Random seed for reproducibility (default: 42).
        stratify: Optional column name for stratification (e.g., 'State').
                  If provided, must exist in data.columns.

    Returns:
        DataFrame with added 'fold' column (0 to n_folds-1).
        Each row is assigned to exactly one fold.

    Raises:
        ValueError: If data is empty, n_folds is invalid, or stratify column doesn't exist.
        TypeError: If data is not a DataFrame.
    """
    # Validate inputs
    if not isinstance(data, pd.DataFrame):
        raise TypeError(f"data must be pandas DataFrame, got {type(data)}")

    if len(data) == 0:
        raise ValueError("data cannot be empty")

    if not isinstance(n_folds, int) or n_folds < 2:
        raise ValueError(f"n_folds must be integer >= 2, got {n_folds}")

    if n_folds > len(data):
        raise ValueError(
            f"n_folds ({n_folds}) cannot be greater than number of samples ({len(data)})"
        )

    if stratify is not None:
        if not isinstance(stratify, str):
            raise TypeError(f"stratify must be string, got {type(stratify)}")
        if stratify not in data.columns:
            raise ValueError(f"stratify column '{stratify}' not found in data.columns")

    data = data.copy()

    # Create KFold splitter
    kfold = KFold(n_splits=n_folds, shuffle=shuffle, random_state=random_state)

    # Initialize fold column
    data['fold'] = None

    # Get indices for splitting
    if stratify is not None and stratify in data.columns:
        # Stratified split
        skfold = StratifiedKFold(n_splits=n_folds, shuffle=shuffle, random_state=random_state)
        splitter = skfold.split(data.index, data[stratify])
    else:
        # Regular KFold
        splitter = kfold.split(data.index)

    # Assign fold numbers
    for fold_num, (train_idx, val_idx) in enumerate(splitter):
        data.loc[data.index[val_idx], 'fold'] = fold_num

    # Verify all rows have fold assigned
    if data['fold'].isna().any():
        raise RuntimeError("Some rows were not assigned to a fold")

    logger.info(f"Created {n_folds}-fold CV splits")
    logger.info(f"Fold distribution:\n{data['fold'].value_counts().sort_index()}")

    return data


def get_fold_data(
    data: pd.DataFrame,
    fold: int,
    train: bool = True
) -> pd.DataFrame:
    """
    Get data for a specific fold (training or validation).

    Args:
        data: DataFrame with 'fold' column. Must not be empty.
        fold: Fold number (0 to n_folds-1). Must be valid fold number.
        train: If True, return training data (all folds except specified).
               If False, return validation data (only the specified fold).

    Returns:
        Filtered DataFrame containing either training or validation data.
        Returns empty DataFrame if fold doesn't exist in data.

    Raises:
        ValueError: If data is empty, doesn't have 'fold' column, or fold is invalid.
        TypeError: If data is not a DataFrame.
    """
    # Validate inputs
    if not isinstance(data, pd.DataFrame):
        raise TypeError(f"data must be pandas DataFrame, got {type(data)}")

    if len(data) == 0:
        raise ValueError("data cannot be empty")

    if 'fold' not in data.columns:
        raise ValueError("data must have 'fold' column")

    if not isinstance(fold, int) or fold < 0:
        raise ValueError(f"fold must be non-negative integer, got {fold}")

    if train:
        # Training data: all folds except the specified fold
        filtered = data[data['fold'] != fold].copy()
        logger.debug(f"Fold {fold} training data: {len(filtered)} samples")
    else:
        # Validation data: only the specified fold
        filtered = data[data['fold'] == fold].copy()
        logger.debug(f"Fold {fold} validation data: {len(filtered)} samples")

        if len(filtered) == 0:
            logger.warning(f"No data found for fold {fold} (validation)")

    return filtered
