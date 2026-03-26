"""Color jittering augmentations. Callers pass params (e.g. from contest transform_defaults)."""

import torchvision.transforms as transforms

from typing import Optional

from level_0 import get_logger

logger = get_logger(__name__)


def get_color_jitter_transform(
    brightness: Optional[float] = 0.2,
    contrast: Optional[float] = 0.2,
    saturation: Optional[float] = 0.2,
    hue: Optional[float] = 0.1,
    p: float = 1.0,
) -> transforms.ColorJitter:
    """
    Get color jitter transform. When p < 1, wraps in RandomApply. Caller passes params.
    """
    if brightness is not None and brightness < 0:
        raise ValueError(f"brightness must be non-negative, got {brightness}")
    if contrast is not None and contrast < 0:
        raise ValueError(f"contrast must be non-negative, got {contrast}")
    if saturation is not None and saturation < 0:
        raise ValueError(f"saturation must be non-negative, got {saturation}")
    if hue is not None and not (0.0 <= hue <= 0.5):
        raise ValueError(f"hue must be in [0, 0.5], got {hue}")

    t = transforms.ColorJitter(
        brightness=brightness,
        contrast=contrast,
        saturation=saturation,
        hue=hue,
    )
    if p < 1.0:
        return transforms.RandomApply([t], p=p)
    return t
