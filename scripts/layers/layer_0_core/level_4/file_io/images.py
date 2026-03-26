"""Image loading utilities using PIL/Pillow."""

from pathlib import Path
from typing import Union, Optional
from PIL import Image

from level_0 import get_logger, DataLoadError, DataProcessingError, ensure_dir, load_image_pil
from level_3 import validate_path_is_file

logger = get_logger(__name__)


def load_image_raw(path: Union[str, Path]) -> Image.Image:
    """
    Load image without validation.
    
    Args:
        path: Path to image file
        
    Returns:
        Loaded PIL Image
    """
    return Image.open(Path(path))


def load_image(
    path: Union[str, Path],
    *,
    convert_rgb: bool = True,
) -> Image.Image:
    """
    Load a single image from disk using PIL.

    Args:
        path: Path to image file.
        convert_rgb: Convert image to RGB if not already (default: True).

    Returns:
        Loaded PIL Image in specified mode.
        
    Raises:
        FileNotFoundError: If image file doesn't exist
        DataLoadError: If image cannot be opened or converted
        
    Example:
        >>> image = load_image('photo.jpg', convert_rgb=True)
        >>> image.size
        (1920, 1080)
    """
    try:
        path_obj = validate_path_is_file(path, name="Image file")
    except Exception as e:
        raise DataLoadError(f"Invalid image path: {e}")

    try:
        image = load_image_pil(path_obj, convert_rgb=convert_rgb)
        logger.debug(
            f"Loaded image: {path_obj} "
            f"(mode={image.mode}, size={image.size})"
        )
        return image

    except Exception as e:
        logger.error(f"Failed to load image: {path_obj}", exc_info=True)
        raise DataLoadError(f"Failed to load image {path_obj}: {e}")


def save_image(
    image: Image.Image,
    path: Union[str, Path],
    format: Optional[str] = None,
    **kwargs
) -> None:
    """
    Save PIL Image to disk.
    
    Args:
        image: PIL Image to save
        path: Path where to save image
        format: Optional format (e.g., 'JPEG', 'PNG'). Auto-detected from extension if None.
        **kwargs: Additional arguments passed to Image.save()
        
    Raises:
        DataProcessingError: If save fails
        
    Example:
        >>> save_image(img, 'output.png')
        >>> save_image(img, 'photo.jpg', quality=95)
    """
    path = Path(path)
    try:
        ensure_dir(path.parent)
        image.save(path, format=format, **kwargs)
        logger.debug(f"Saved image: {path}")
    except Exception as e:
        raise DataProcessingError(f"Failed to save image {path}: {e}")