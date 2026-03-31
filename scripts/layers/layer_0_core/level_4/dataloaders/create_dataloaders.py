"""DataLoader creation utilities."""

import pandas as pd

from typing import Tuple, Optional, Callable, Any

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_2 import (
    build_preprocessing_transforms,
    create_dataloader_from_dataset,
    create_dataset_for_test_dataloader,
    create_datasets_for_dataloaders,
    create_worker_init_fn,
    validate_dataframe,
)
from layers.layer_0_core.level_3 import build_transforms_for_dataloaders

logger = get_logger(__name__)


def create_dataloaders(
    train_data: pd.DataFrame,
    val_data: pd.DataFrame,
    image_dir: str,
    image_col: str = 'image_id',
    target_cols: Optional[list] = None,
    image_size: int = 224,
    batch_size: int = 32,
    num_workers: int = 4,
    pin_memory: bool = True,
    augmentation: str = 'medium',
    train_transform: Optional[Callable] = None,
    val_transform: Optional[Callable] = None,
    seed: int = 42
) -> Tuple[Any, Any]:
    """
    Create training and validation data loaders.
    
    Args:
        train_data: Training DataFrame with image IDs and targets.
        val_data: Validation DataFrame with image IDs and targets.
        image_dir: Directory containing images.
        image_col: Column name for image IDs (default: 'image_id').
        target_cols: List of target column names. If None, no targets returned.
        image_size: Target image size for transforms (default: 224).
        batch_size: Batch size for both train and val (default: 32).
        num_workers: Number of data loading workers (default: 4).
        pin_memory: Whether to pin memory for faster GPU transfer (default: True).
        augmentation: Augmentation preset for training ('none', 'light', 'medium', 'heavy').
        train_transform: Optional custom transform for training (overrides augmentation).
        val_transform: Optional custom transform for validation.
        seed: Random seed for reproducibility (default: 42).
        
    Returns:
        Tuple of (train_loader, val_loader).
        
    Raises:
        ValueError: If data is invalid or empty.
    
    Example:
        >>> train_loader, val_loader = create_dataloaders(
        ...     train_df,
        ...     val_df,
        ...     image_dir='/path/to/images',
        ...     target_cols=['target1', 'target2'],
        ...     batch_size=64
        ... )
    """
    validate_dataframe(train_data, name="train_data", required_columns=[image_col], min_rows=1)
    validate_dataframe(val_data, name="val_data", required_columns=[image_col], min_rows=1)

    # Build transforms if not provided
    train_transform, val_transform = build_transforms_for_dataloaders(
        image_size, augmentation, train_transform, val_transform
    )
    
    # Create datasets
    train_dataset, val_dataset = create_datasets_for_dataloaders(
        train_data, val_data, image_dir, image_col, target_cols,
        train_transform, val_transform
    )
    
    worker_init_fn = create_worker_init_fn(seed)

    train_loader = create_dataloader_from_dataset(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=pin_memory,
        worker_init_fn=worker_init_fn,
    )
    val_loader = create_dataloader_from_dataset(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
        worker_init_fn=worker_init_fn,
    )
    
    logger.info(f"✅ Created data loaders:")
    logger.info(f"  Train: {len(train_dataset)} samples, {len(train_loader)} batches")
    logger.info(f"  Val: {len(val_dataset)} samples, {len(val_loader)} batches")
    logger.info(f"  Batch size: {batch_size}, Num workers: {num_workers}")
    
    return train_loader, val_loader


def create_test_dataloader(
    test_data: pd.DataFrame,
    image_dir: str,
    image_col: str = 'image_id',
    image_size: int = 224,
    batch_size: int = 32,
    num_workers: int = 4,
    pin_memory: bool = True,
    test_transform: Optional[Callable] = None
) -> Any:
    """
    Create test data loader (no targets).
    
    Args:
        test_data: Test DataFrame with image IDs.
        image_dir: Directory containing images.
        image_col: Column name for image IDs (default: 'image_id').
        image_size: Target image size for transforms (default: 224).
        batch_size: Batch size (default: 32).
        num_workers: Number of data loading workers (default: 4).
        pin_memory: Whether to pin memory for faster GPU transfer (default: True).
        test_transform: Optional custom transform. If None, uses default val transform.
        
    Returns:
        Test DataLoader.
    
    Example:
        >>> test_loader = create_test_dataloader(
        ...     test_df,
        ...     image_dir='/path/to/images'
        ... )
    """
    validate_dataframe(test_data, name="test_data", required_columns=[image_col], min_rows=1)

    if test_transform is None:
        test_transform = build_preprocessing_transforms(image_size)

    test_dataset = create_dataset_for_test_dataloader(
        test_data, image_dir, image_col, test_transform
    )
    test_loader = create_dataloader_from_dataset(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=pin_memory,
    )
    
    logger.info(f"✅ Created test loader: {len(test_dataset)} samples, {len(test_loader)} batches")
    
    return test_loader
