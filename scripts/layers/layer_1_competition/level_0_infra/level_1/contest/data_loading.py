"""Contest data loading facade to reduce deep imports.

This module provides a clean interface for contest-specific data loading operations,
reducing deep cross-package imports and improving package cohesion.
"""

import pandas as pd

from typing import Optional, Any, Tuple
from pathlib import Path
from sklearn.model_selection import train_test_split

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import create_kfold_splits, get_fold_data

from ..registry import ContestRegistry, get_contest

logger = get_logger(__name__)


def load_contest_training_data(
    contest_name: str,
    train_csv_path: Path,
    validation_split: Optional[float] = None,
    n_folds: Optional[int] = None,
    fold: Optional[int] = None
) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]:
    """
    Load training data for a contest with contest-specific handling.

    Uses registry dispatch: contests may register a training_data_loader.
    Falls back to pd.read_csv when no loader is registered.
    """
    contest_entry = ContestRegistry.get(contest_name) or {}
    loader_fn = contest_entry.get('training_data_loader')
    train_data = loader_fn(train_csv_path) if loader_fn else pd.read_csv(train_csv_path)

    val_data = None
    if n_folds is not None and n_folds > 1:
        train_data = create_kfold_splits(
            train_data, n_folds=n_folds, shuffle=True, random_state=42
        )
        if fold is not None:
            val_data = get_fold_data(train_data, fold=fold, train=False)
            train_data = get_fold_data(train_data, fold=fold, train=True)
    elif validation_split is not None and 0 < validation_split < 1:
        train_data, val_data = train_test_split(
            train_data, test_size=validation_split, random_state=42
        )

    return train_data, val_data


def load_contest_data(
    contest_name: str,
    model_type: str,
    validation_split: Optional[float] = None,
    n_folds: Optional[int] = None,
    fold: Optional[int] = None
) -> tuple:
    """
    Load training and validation data from contest paths.

    Uses facade to avoid deep imports to contest implementations.

    Args:
        contest_name: Contest name (e.g., 'csiro', 'cafa')
        model_type: Model type ('vision' or 'tabular')
        validation_split: Validation split ratio (0.0 to 1.0). If None, uses CV folds.
        n_folds: Number of CV folds (used if validation_split is None)
        fold: Specific fold to use for validation (0 to n_folds-1). If None, uses first fold.

    Returns:
        Tuple of (train_data, val_data, test_data):
        - train_data: Training DataFrame
        - val_data: Validation DataFrame (None if no validation split)
        - test_data: Test DataFrame (None if not available)
    """
    contest = get_contest(contest_name)
    paths = contest['paths']()

    data_root = paths.local_data_root
    train_csv_path = data_root / 'train.csv'
    test_csv_path = data_root / 'test.csv'

    train_data = None
    val_data = None

    # Load training data
    if train_csv_path.exists():
        if model_type == 'vision':
            train_data, val_data = load_contest_training_data(
                contest_name, train_csv_path, validation_split, n_folds, fold
            )
        else:  # tabular
            train_data, val_data = _load_tabular_data(train_csv_path, validation_split)
    else:
        logger.warning(f"Training CSV not found: {train_csv_path}")

    # Load test data
    test_data = _load_test_data(test_csv_path)

    return train_data, val_data, test_data


def _load_tabular_data(  # only used in load_contest_data
    train_csv_path: Path,
    validation_split: Optional[float] = None
) -> tuple[Any, Any]:
    """
    Load tabular training data.

    Args:
        train_csv_path: Path to training CSV
        validation_split: Validation split ratio (0.0 to 1.0)

    Returns:
        Tuple of (train_data, val_data)
    """

    train_data = pd.read_csv(train_csv_path)
    val_data = None

    if validation_split is not None and 0 < validation_split < 1:
        train_data, val_data = train_test_split(train_data, test_size=validation_split, random_state=42)

    return train_data, val_data


def _load_test_data(test_csv_path: Path) -> Any:  # only used in load_contest_data
    """
    Load test data from CSV file.

    Args:
        test_csv_path: Path to test CSV file

    Returns:
        Test DataFrame if file exists, None otherwise
    """
    if test_csv_path.exists():
        return pd.read_csv(test_csv_path)
    else:
        logger.debug(f"Test CSV not found: {test_csv_path}")
        return None
