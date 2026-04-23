"""Dataset split caching and train/val creation utilities."""

import pandas as pd

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

from layers.layer_0_core.level_0 import ensure_dir, get_logger, is_kaggle
from layers.layer_0_core.level_2 import get_train_test_split
from layers.layer_0_core.level_4 import save_json

_logger = get_logger(__name__)


def get_dataset_cache_dir() -> Path:
    """
    Return the environment-appropriate dataset cache directory.

    Returns:
        /kaggle/working/datasets on Kaggle, output/datasets locally.
    """
    cache_dir = (
        Path("/kaggle/working/datasets") if is_kaggle()
        else Path("output/datasets")
    )
    ensure_dir(cache_dir)
    return cache_dir


def save_dataset_splits(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    cache_key: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Path:
    """
    Persist train/val DataFrames to parquet and optional metadata to JSON.

    Args:
        train_df: Training DataFrame.
        val_df: Validation DataFrame.
        cache_key: Unique identifier for this dataset variant.
        metadata: Optional metadata dict to persist alongside the splits.

    Returns:
        Path to the variant cache directory.
    """
    variant_dir = get_dataset_cache_dir() / cache_key
    ensure_dir(variant_dir)

    train_df.to_parquet(variant_dir / 'train.parquet', index=False)
    val_df.to_parquet(variant_dir / 'val.parquet', index=False)

    _logger.info("Saved dataset splits to %s", variant_dir)
    _logger.info("  Train: %s samples", len(train_df))
    _logger.info("  Val: %s samples", len(val_df))

    if metadata:
        save_json(metadata, variant_dir / 'metadata.json')

    return variant_dir


def load_dataset_splits(cache_key: str) -> Optional[Tuple[pd.DataFrame, pd.DataFrame]]:
    """
    Load cached train/val splits if they exist.

    Args:
        cache_key: Unique identifier for the dataset variant.

    Returns:
        (train_df, val_df) if both parquet files exist, else None.
    """
    variant_dir = get_dataset_cache_dir() / cache_key
    train_path = variant_dir / 'train.parquet'
    val_path = variant_dir / 'val.parquet'

    if not train_path.exists() or not val_path.exists():
        return None

    try:
        train_df = pd.read_parquet(train_path)
        val_df = pd.read_parquet(val_path)
        _logger.info("Loaded cached dataset splits from %s", variant_dir)
        _logger.info("  Train: %s samples", len(train_df))
        _logger.info("  Val: %s samples", len(val_df))
        return train_df, val_df
    except Exception as e:
        _logger.warning("Failed to load cached splits from %s: %s", variant_dir, e)
        return None


def apply_train_val_split(
    data: Any,
    validation_split: float,
    random_state: int = 42,
) -> Tuple[Any, Any]:
    """
    Split data into train and validation subsets.

    Args:
        data: DataFrame or array to split.
        validation_split: Fraction to reserve for validation (0.0–1.0).
        random_state: Seed for reproducibility.

    Returns:
        (train_data, val_data)
    """
    train_test_split = get_train_test_split()
    return train_test_split(
        data,
        test_size=validation_split,
        random_state=random_state,
        shuffle=True,
    )