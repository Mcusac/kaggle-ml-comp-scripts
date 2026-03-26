"""Utilities for getting checkpoint and model paths."""

from pathlib import Path
from typing import Union


def _validate_fold_path_args(model_dir: Union[str, Path, None], fold: int) -> Path:
    """Validate model_dir and fold; return Path(model_dir)."""
    if model_dir is None:
        raise ValueError("model_dir cannot be None")
    if not isinstance(fold, int) or fold < 0:
        raise ValueError(f"fold must be non-negative integer, got {fold}")
    return Path(model_dir)


def _get_fold_dir(base: Path, fold: int) -> Path:
    """Return path to fold subdirectory: base/fold_{fold}."""
    return base / f'fold_{fold}'


def get_fold_checkpoint_path(model_dir: Path, fold: int) -> Path:
    """
    Get the standard checkpoint path for a fold.

    Args:
        model_dir: Path to base model directory.
        fold: Fold number (0 to n_folds-1). Must be non-negative integer.

    Returns:
        Path to fold checkpoint: {model_dir}/fold_{fold}/best_model.pth

    Raises:
        ValueError: If fold is negative.
        TypeError: If model_dir or fold have invalid types.
    """
    base = _validate_fold_path_args(model_dir, fold)
    return _get_fold_dir(base, fold) / 'best_model.pth'


def get_fold_regression_model_path(model_dir: Path, fold: int) -> Path:
    """
    Get the regression model path for a fold (feature extraction mode).

    Args:
        model_dir: Path to base model directory.
        fold: Fold number (0 to n_folds-1). Must be non-negative integer.

    Returns:
        Path to regression model: {model_dir}/fold_{fold}/regression_model.pkl

    Raises:
        ValueError: If fold is negative.
        TypeError: If model_dir or fold have invalid types.
    """
    base = _validate_fold_path_args(model_dir, fold)
    return _get_fold_dir(base, fold) / 'regression_model.pkl'