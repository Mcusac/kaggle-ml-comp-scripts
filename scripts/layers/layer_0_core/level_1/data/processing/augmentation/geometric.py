"""Geometric transformation augmentations. Callers pass params (e.g. from contest transform_defaults)."""

import torchvision.transforms as transforms

from typing import Optional, Tuple, Union

from layers.layer_0_core.level_0 import get_logger

_logger = get_logger(__name__)


def get_geometric_transform(
    degrees: Union[float, Tuple[float, float]] = 15.0,
    translate: Optional[Tuple[float, float]] = (0.1, 0.1),
    scale: Optional[Tuple[float, float]] = (0.9, 1.1),
    shear: Optional[Union[float, Tuple[float, float]]] = 5.0,
    interpolation: transforms.InterpolationMode = transforms.InterpolationMode.BILINEAR,
    fill: int = 0,
    p: float = 1.0,
) -> transforms.RandomAffine:
    """
    Get geometric transformation (rotation, translation, scale, shear).
    When p < 1, wraps in RandomApply. Caller passes params.
    """
    if translate is not None:
        if len(translate) != 2:
            raise ValueError(f"translate must be a tuple of length 2, got {translate}")
        if not all(0.0 <= v <= 1.0 for v in translate):
            raise ValueError(f"translate values must be in [0, 1], got {translate}")
    if scale is not None:
        if len(scale) != 2:
            raise ValueError(f"scale must be a tuple of length 2, got {scale}")
        if scale[0] >= scale[1]:
            raise ValueError(f"scale[0] must be < scale[1], got {scale}")
        if not all(v > 0 for v in scale):
            raise ValueError(f"scale values must be positive, got {scale}")

    t = transforms.RandomAffine(
        degrees=degrees,
        translate=translate,
        scale=scale,
        shear=shear,
        interpolation=interpolation,
        fill=fill,
    )
    if p < 1.0:
        return transforms.RandomApply([t], p=p)
    return t
