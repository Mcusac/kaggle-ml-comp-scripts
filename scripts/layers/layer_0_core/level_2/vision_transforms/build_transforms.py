"""Preprocessing and training/validation transform pipeline construction."""

import torchvision.transforms as transforms

from typing import List, Optional, Tuple, Union

from level_0 import get_logger, IMAGENET_MEAN, IMAGENET_STD
from level_1 import get_resize_transform, get_normalize_transform

logger = get_logger(__name__)


def build_preprocessing_transforms(
    image_size: Union[int, Tuple[int, int]],
    normalize: bool = True,
    mean: Tuple[float, float, float] = IMAGENET_MEAN,
    std: Tuple[float, float, float] = IMAGENET_STD,
    center_crop: bool = False,
    additional_transforms: Optional[List] = None,
) -> transforms.Compose:
    """
    Build a preprocessing transform pipeline.

    Standard pipeline: resize, optional center crop, optional extra transforms,
    ToTensor, optional normalization.
    """
    transform_list = []

    if image_size:
        transform_list.append(get_resize_transform(image_size))
        logger.debug(f"Added resize transform: {image_size}")

    if center_crop:
        crop_size = image_size if isinstance(image_size, int) else image_size[0]
        transform_list.append(transforms.CenterCrop(crop_size))
        logger.debug(f"Added center crop: {crop_size}")

    if additional_transforms:
        transform_list.extend(additional_transforms)
        logger.debug(f"Added {len(additional_transforms)} additional transforms")

    transform_list.append(transforms.ToTensor())

    if normalize:
        transform_list.append(get_normalize_transform(mean, std))
        logger.debug(f"Added normalization: mean={mean}, std={std}")

    return transforms.Compose(transform_list)


def build_simple_transforms(
    image_size: Union[int, Tuple[int, int]],
    normalize: bool = False,
) -> transforms.Compose:
    """Build a minimal transform pipeline (resize + ToTensor only)."""
    transform_list = [
        get_resize_transform(image_size),
        transforms.ToTensor(),
    ]

    if normalize:
        transform_list.append(get_normalize_transform())

    return transforms.Compose(transform_list)
