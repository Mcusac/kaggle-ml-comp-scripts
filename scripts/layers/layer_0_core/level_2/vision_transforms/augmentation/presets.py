"""Common augmentation presets and preset selector."""

import torchvision.transforms as transforms

from typing import List, Any, Optional, Literal

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import get_geometric_transform, get_color_jitter_transform, get_blur_transform

logger = get_logger(__name__)


def get_light_augmentation() -> List[Any]:
    """Get light augmentation preset (minimal augmentation)."""
    return [
        transforms.RandomHorizontalFlip(p=0.5),
    ]


def get_medium_augmentation() -> List[Any]:
    """Get medium augmentation preset (moderate augmentation for training)."""
    return [
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        get_geometric_transform(
            degrees=10.0,
            translate=(0.05, 0.05),
            scale=(0.95, 1.05),
            shear=None
        ),
        get_color_jitter_transform(
            brightness=0.1,
            contrast=0.1,
            saturation=0.1,
            hue=0.05
        ),
    ]


def get_heavy_augmentation() -> List[Any]:
    """Get heavy augmentation preset (aggressive augmentation)."""
    return [
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.5),
        get_geometric_transform(
            degrees=20.0,
            translate=(0.1, 0.1),
            scale=(0.9, 1.1),
            shear=10.0
        ),
        get_color_jitter_transform(
            brightness=0.3,
            contrast=0.3,
            saturation=0.3,
            hue=0.15
        ),
        transforms.RandomApply([get_blur_transform(kernel_size=3, sigma=(0.1, 2.0))], p=0.3),
    ]


def get_custom_augmentation(
    horizontal_flip: bool = True,
    vertical_flip: bool = False,
    rotation_degrees: float = 0.0,
    color_jitter: bool = False,
    blur: bool = False
) -> List[Any]:
    """Build custom augmentation pipeline from individual components."""
    transforms_list = []
    if horizontal_flip:
        transforms_list.append(transforms.RandomHorizontalFlip(p=0.5))
    if vertical_flip:
        transforms_list.append(transforms.RandomVerticalFlip(p=0.5))
    if rotation_degrees > 0:
        transforms_list.append(
            get_geometric_transform(
                degrees=rotation_degrees,
                translate=None,
                scale=None,
                shear=None
            )
        )
    if color_jitter:
        transforms_list.append(get_color_jitter_transform())
    if blur:
        transforms_list.append(
            transforms.RandomApply([get_blur_transform()], p=0.3)
        )
    return transforms_list


AugmentationPreset = Literal['none', 'light', 'medium', 'heavy']

PRESET_FUNCS = {
    'none': lambda: [],
    'light': get_light_augmentation,
    'medium': get_medium_augmentation,
    'heavy': get_heavy_augmentation,
}


def build_augmentation_transforms(
    preset: AugmentationPreset = 'none',
    additional_transforms: Optional[List] = None
) -> List[Any]:
    """
    Build augmentation transform pipeline from preset or custom transforms.

    Args:
        preset: Augmentation preset ('none', 'light', 'medium', 'heavy').
        additional_transforms: Optional list of additional transforms to append.

    Returns:
        List of transform instances for augmentation.

    Raises:
        ValueError: If preset is not recognized.
    """
    if preset not in PRESET_FUNCS:
        raise ValueError(
            f"Unknown augmentation preset: '{preset}'. "
            f"Must be one of: 'none', 'light', 'medium', 'heavy'"
        )
    transform_list = list(PRESET_FUNCS[preset]())

    if additional_transforms:
        transform_list.extend(additional_transforms)
        logger.debug(f"Added {len(additional_transforms)} additional transforms to {preset} preset")

    logger.debug(f"Built augmentation pipeline with {len(transform_list)} transforms (preset: {preset})")

    return transform_list
