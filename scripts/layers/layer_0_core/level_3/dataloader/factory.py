"""DataLoader factory for creating train/val dataloaders from config."""

import pandas as pd

from typing import Any, Callable, Dict, Optional, Tuple, Union

from layers.layer_0_core.level_0 import get_logger, get_torch
from layers.layer_0_core.level_1 import StreamingDataset, StreamingSplitDataset
from layers.layer_0_core.level_2 import (
    AugmentationPreset,
    build_augmentation_transforms,
    build_preprocessing_transforms,
)

_torch = get_torch()
_DataLoader = _torch.utils.data.DataLoader
_logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _extract_loader_settings(
    config: Union[Any, Dict[str, Any]],
    batch_size: Optional[int],
    num_workers: Optional[int],
    pin_memory: Optional[bool],
) -> Tuple[int, int, bool]:
    """
    Resolve batch_size, num_workers, and pin_memory from explicit args or config.

    Explicit args take priority. Falls back to config attributes, then config
    dict keys, then hardcoded defaults.
    """
    if hasattr(config, 'training'):
        batch_size = batch_size if batch_size is not None else config.training.batch_size
    elif isinstance(config, dict):
        batch_size = batch_size if batch_size is not None else config.get('batch_size', 32)
    else:
        batch_size = batch_size if batch_size is not None else 32

    if hasattr(config, 'device'):
        num_workers = num_workers if num_workers is not None else config.device.num_workers
        pin_memory = pin_memory if pin_memory is not None else config.device.pin_memory
    elif isinstance(config, dict):
        num_workers = num_workers if num_workers is not None else config.get('num_workers', 4)
        pin_memory = pin_memory if pin_memory is not None else config.get('pin_memory', True)
    else:
        num_workers = num_workers if num_workers is not None else 4
        pin_memory = pin_memory if pin_memory is not None else True

    return batch_size, num_workers, pin_memory


def _extract_target_info(
    config: Union[Any, Dict[str, Any]],
) -> Tuple[Optional[list], str]:
    """
    Resolve target_cols and image_path_column from config.

    Returns:
        Tuple of (target_cols, image_path_column).
    """
    target_cols = None
    if hasattr(config, 'primary_targets'):
        target_cols = config.primary_targets
    elif isinstance(config, dict):
        target_cols = config.get('primary_targets')

    image_path_column = 'image_path'
    if hasattr(config, 'image_path_column'):
        image_path_column = config.image_path_column
    elif isinstance(config, dict):
        image_path_column = config.get('image_path_column', 'image_path')

    return target_cols, image_path_column


def _build_dataloader(
    data: pd.DataFrame,
    data_root: str,
    transform: Callable,
    dataset_type: str,
    batch_size: int,
    num_workers: int,
    pin_memory: bool,
    shuffle: bool,
    target_cols: Optional[list],
    image_path_column: str,
    **kwargs,
) -> _DataLoader:
    """Construct a dataset and wrap it in a DataLoader."""
    DatasetClass = StreamingSplitDataset if dataset_type == 'split' else StreamingDataset
    dataset = DatasetClass(
        data,
        data_root=data_root,
        transform=transform,
        target_cols=target_cols,
        shuffle=shuffle,
        image_path_column=image_path_column,
    )
    return _DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=False,  # Shuffle is handled inside IterableDataset
        num_workers=num_workers,
        pin_memory=pin_memory,
        **kwargs,
    )


def _create_dataloader_from_config(
    data: pd.DataFrame,
    data_root: str,
    config: Union[Any, Dict[str, Any]],
    image_size: Tuple[int, int],
    transform: Optional[Callable],
    augmentation: AugmentationPreset,
    shuffle: bool,
    batch_size: Optional[int],
    dataset_type: str,
    num_workers: Optional[int],
    pin_memory: Optional[bool],
    **kwargs,
) -> _DataLoader:
    """
    Shared implementation for train and validation dataloader creation.

    Resolves settings from config, builds the transform if not provided,
    and constructs the DataLoader.

    Args:
        data: DataFrame with image path column and target columns.
        data_root: Root directory for images.
        config: Configuration object or dict with training/device settings.
        image_size: Target image size as (height, width).
        transform: Pre-built transform; if None, one is built from image_size
                   and augmentation.
        augmentation: Augmentation preset used when building the transform.
                      Ignored when transform is provided.
        shuffle: Whether to shuffle the dataset.
        batch_size: Override batch size from config.
        dataset_type: Dataset variant ('split' or 'full').
        num_workers: Override num_workers from config.
        pin_memory: Override pin_memory from config.
        **kwargs: Additional arguments forwarded to DataLoader.

    Returns:
        Configured DataLoader instance.
    """
    batch_size, num_workers, pin_memory = _extract_loader_settings(
        config, batch_size, num_workers, pin_memory
    )
    target_cols, image_path_column = _extract_target_info(config)

    if transform is None:
        augmentation_list = build_augmentation_transforms(preset=augmentation)
        transform = build_preprocessing_transforms(
            image_size,
            additional_transforms=augmentation_list if augmentation_list else None,
        )

    return _build_dataloader(
        data, data_root, transform, dataset_type,
        batch_size, num_workers, pin_memory,
        shuffle=shuffle,
        target_cols=target_cols,
        image_path_column=image_path_column,
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def create_train_dataloader(
    train_data: pd.DataFrame,
    data_root: str,
    config: Union[Any, Dict[str, Any]],
    image_size: Tuple[int, int],
    batch_size: Optional[int] = None,
    dataset_type: str = 'split',
    num_workers: Optional[int] = None,
    pin_memory: Optional[bool] = None,
    train_transform: Optional[Callable] = None,
    augmentation: AugmentationPreset = 'light',
    **kwargs,
) -> _DataLoader:
    """
    Create a training DataLoader from config.

    Args:
        train_data: Training DataFrame with an image path column and target columns.
        data_root: Root directory for images.
        config: Configuration object or dict with training/device settings.
        image_size: Target image size as (height, width).
        batch_size: Override batch size from config.
        dataset_type: Dataset variant ('split' or 'full', default: 'split').
        num_workers: Override num_workers from config.
        pin_memory: Override pin_memory from config.
        train_transform: Pre-built transform; if None, one is built from
                         image_size and augmentation.
        augmentation: Augmentation preset when building the transform.
                      One of 'none', 'light', 'medium', 'heavy' (default: 'light').
                      Ignored when train_transform is provided.
        **kwargs: Additional arguments forwarded to DataLoader.

    Returns:
        Training DataLoader instance.
    """
    loader = _create_dataloader_from_config(
        train_data, data_root, config, image_size,
        transform=train_transform,
        augmentation=augmentation,
        shuffle=True,
        batch_size=batch_size,
        dataset_type=dataset_type,
        num_workers=num_workers,
        pin_memory=pin_memory,
        **kwargs,
    )
    _logger.info(f"Created training dataloader: {len(loader)} batches, batch_size={loader.batch_size}")
    return loader


def create_val_dataloader(
    val_data: pd.DataFrame,
    data_root: str,
    config: Union[Any, Dict[str, Any]],
    image_size: Tuple[int, int],
    batch_size: Optional[int] = None,
    dataset_type: str = 'split',
    num_workers: Optional[int] = None,
    pin_memory: Optional[bool] = None,
    val_transform: Optional[Callable] = None,
    **kwargs,
) -> _DataLoader:
    """
    Create a validation DataLoader from config.

    Args:
        val_data: Validation DataFrame with an image path column and target columns.
        data_root: Root directory for images.
        config: Configuration object or dict with training/device settings.
        image_size: Target image size as (height, width).
        batch_size: Override batch size from config.
        dataset_type: Dataset variant ('split' or 'full', default: 'split').
        num_workers: Override num_workers from config.
        pin_memory: Override pin_memory from config.
        val_transform: Pre-built transform; if None, a preprocessing-only
                       transform is built from image_size (no augmentation).
        **kwargs: Additional arguments forwarded to DataLoader.

    Returns:
        Validation DataLoader instance.
    """
    loader = _create_dataloader_from_config(
        val_data, data_root, config, image_size,
        transform=val_transform,
        augmentation='none',
        shuffle=False,
        batch_size=batch_size,
        dataset_type=dataset_type,
        num_workers=num_workers,
        pin_memory=pin_memory,
        **kwargs,
    )
    _logger.info(f"Created validation dataloader: {len(loader)} batches, batch_size={loader.batch_size}")
    return loader