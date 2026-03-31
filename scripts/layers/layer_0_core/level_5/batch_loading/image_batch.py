"""Batch loading for images. Uses level_1.load_batch and level_4.load_image."""

from pathlib import Path
from typing import Iterable, List, Union

from PIL import Image

from layers.layer_0_core.level_1 import load_batch
from layers.layer_0_core.level_4 import load_image


def load_image_batch(
    paths: Iterable[Union[str, Path]],
    *,
    convert_rgb: bool = True,
    show_progress: bool = False,
) -> List[Image.Image]:
    """Load multiple images."""
    loader = lambda path: load_image(path, convert_rgb=convert_rgb)
    return load_batch(
        paths,
        loader,
        desc="Loading images",
        show_progress=show_progress,
        item_name="images",
    )
