"""Transform builders for training and validation dataloaders."""

from typing import Callable, Optional, Tuple

from level_2 import AugmentationPreset, build_augmentation_transforms, build_preprocessing_transforms


def build_transforms_for_dataloaders(
    image_size: int,
    augmentation: AugmentationPreset,
    train_transform: Optional[Callable],
    val_transform: Optional[Callable],
) -> Tuple[Callable, Callable]:
    """
    Build train and validation transforms, respecting any pre-built overrides.

    When train_transform or val_transform is provided it is returned unchanged.
    Otherwise a transform is constructed from image_size and augmentation.
    Validation always uses preprocessing only (no augmentation).

    Args:
        image_size: Target image size passed to build_preprocessing_transforms.
        augmentation: Augmentation preset for training. One of 'none', 'light',
                      'medium', 'heavy'.
        train_transform: Pre-built training transform, or None to build one.
        val_transform: Pre-built validation transform, or None to build one.

    Returns:
        Tuple of (train_transform, val_transform).
    """
    if train_transform is None:
        augmentation_list = build_augmentation_transforms(preset=augmentation)
        train_transform = build_preprocessing_transforms(
            image_size,
            additional_transforms=augmentation_list if augmentation_list else None,
        )

    if val_transform is None:
        val_transform = build_preprocessing_transforms(image_size)

    return train_transform, val_transform
