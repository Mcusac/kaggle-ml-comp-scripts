"""Contest data loading facade to reduce deep imports.

This module provides a clean interface for contest-specific data loading operations,
reducing deep cross-package imports and improving package cohesion.
"""

import pandas as pd

from pathlib import Path
from typing import Optional, Tuple

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_4 import load_csv_raw, load_csv_raw_if_exists

from layers.layer_1_competition.level_0_infra.level_1.contest.csv_io import (
    load_training_csv,
)
from layers.layer_1_competition.level_0_infra.level_1.contest.splits import split_train_val
from layers.layer_1_competition.level_0_infra.level_1.registry import (
    ContestRegistry,
    get_contest,
)

_logger = get_logger(__name__)


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
    train_data = load_training_csv(contest_entry=contest_entry, train_csv_path=train_csv_path)
    train_data, val_data = split_train_val(
        train_data=train_data,
        validation_split=validation_split,
        n_folds=n_folds,
        fold=fold,
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
            train_data = load_csv_raw(train_csv_path)
            train_data, val_data = split_train_val(
                train_data=train_data,
                validation_split=validation_split,
                n_folds=None,
                fold=None,
            )
    else:
        _logger.warning(f"Training CSV not found: {train_csv_path}")

    # Load test data
    test_data = load_csv_raw_if_exists(test_csv_path)
    if test_data is None:
        _logger.debug(f"Test CSV not found: {test_csv_path}")

    return train_data, val_data, test_data
