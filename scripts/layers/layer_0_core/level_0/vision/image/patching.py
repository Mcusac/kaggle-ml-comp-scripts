"""Image tiling utilities."""

import numpy as np
from typing import List


def split_image(
    image: np.ndarray,
    patch_size: int = 520,
    overlap: int = 16,
) -> List[np.ndarray]:
    """
    Split image into overlapping patches.

    Args:
        image: HWC numpy image
        patch_size: tile size
        overlap: overlap between tiles

    Returns:
        List of patches
    """
    h, w, _ = image.shape
    stride = patch_size - overlap

    patches = []

    for y in range(0, h, stride):
        for x in range(0, w, stride):
            y2 = min(y + patch_size, h)
            x2 = min(x + patch_size, w)

            y1 = max(0, y2 - patch_size)
            x1 = max(0, x2 - patch_size)

            patches.append(image[y1:y2, x1:x2])

    return patches