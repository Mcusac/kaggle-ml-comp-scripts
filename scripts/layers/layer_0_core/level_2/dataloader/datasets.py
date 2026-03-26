"""Dataset construction helpers for training and validation dataloaders."""

import pandas as pd

from typing import Callable, List, Optional, Tuple

from layers.layer_0_core.level_1 import BaseImageDataset


def create_dataset_for_test_dataloader(
    data: pd.DataFrame,
    image_dir: str,
    image_col: str,
    transform: Callable,
) -> BaseImageDataset:
    """
    Create single BaseImageDataset for test inference (no targets).

    Args:
        data: Test DataFrame with image IDs.
        image_dir: Root directory for images.
        image_col: Column name containing image identifiers.
        transform: Transform applied to images.

    Returns:
        BaseImageDataset instance.
    """
    return BaseImageDataset(
        data=data,
        image_dir=image_dir,
        image_col=image_col,
        target_cols=None,
        transform=transform,
    )


def create_datasets_for_dataloaders(
    train_data: pd.DataFrame,
    val_data: pd.DataFrame,
    image_dir: str,
    image_col: str,
    target_cols: Optional[List[str]],
    train_transform: Callable,
    val_transform: Callable,
) -> Tuple[BaseImageDataset, BaseImageDataset]:
    """
    Create paired training and validation datasets.

    Both datasets share the same image_dir, image_col, and target_cols.
    They differ only in their transform and the data slice they receive.

    Args:
        train_data: Training DataFrame.
        val_data: Validation DataFrame.
        image_dir: Root directory for images.
        image_col: Column name containing image identifiers.
        target_cols: Column names for regression/classification targets.
        train_transform: Transform applied to training images.
        val_transform: Transform applied to validation images.

    Returns:
        Tuple of (train_dataset, val_dataset).
    """
    train_dataset = BaseImageDataset(
        data=train_data,
        image_dir=image_dir,
        image_col=image_col,
        target_cols=target_cols,
        transform=train_transform,
    )
    val_dataset = BaseImageDataset(
        data=val_data,
        image_dir=image_dir,
        image_col=image_col,
        target_cols=target_cols,
        transform=val_transform,
    )
    return train_dataset, val_dataset