"""Preprocessing transform builder registry."""

import torchvision.transforms as transforms

from typing import Dict, Callable, Optional, Any

from level_0 import noise_reduction, get_image_size_from_config
from level_1 import get_resize_transform, contrast_enhancement

TransformBuilder = Callable[[Any], Optional[Any]]


def _get_center_crop_transform(config: Any) -> Optional[transforms.CenterCrop]:
    """Get CenterCrop transform based on config image_size."""
    image_size = get_image_size_from_config(config)
    if not image_size:
        return None
    if isinstance(image_size, (tuple, list)):
        size = image_size[0]
    elif isinstance(image_size, int):
        size = image_size
    else:
        return None
    return transforms.CenterCrop(size)


def _get_resize_from_config(config: Any) -> Optional[Any]:
    """Get resize transform from config; returns None if image_size not set."""
    image_size = get_image_size_from_config(config)
    if image_size is None:
        return None
    return get_resize_transform(image_size)


PREPROCESSING_BUILDERS: Dict[str, TransformBuilder] = {
    "resize": _get_resize_from_config,
    "center_crop": _get_center_crop_transform,
    "contrast_enhancement": lambda config: transforms.Lambda(
        lambda img: contrast_enhancement(img, method="histogram_equalization")
    ),
    "noise_reduction": lambda config: transforms.Lambda(
        lambda img: noise_reduction(img, method="gaussian_blur")
    ),
}
