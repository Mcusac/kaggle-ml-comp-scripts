"""Base image dataset classes for DataFrame-based and path-list loading."""

import pandas as pd

from pathlib import Path
from PIL import Image
from typing import Any, Optional, Callable, List, Union, Tuple

from level_0 import get_logger, get_torch

torch = get_torch()
_Dataset = torch.utils.data.Dataset if torch is not None else object
logger = get_logger(__name__)


class BaseImageDataset(_Dataset):
    """
    Base PyTorch Dataset for image data.

    Handles loading images from filesystem and applying transforms.
    Supports both training (with targets) and inference (without targets) modes.
    """

    def __init__(
        self,
        data: pd.DataFrame,
        image_dir: Union[str, Path],
        image_col: str = 'image_id',
        target_cols: Optional[List[str]] = None,
        transform: Optional[Callable] = None,
        image_ext: str = '.jpg'
    ):
        self.data = data.reset_index(drop=True)
        self.image_dir = Path(image_dir)
        self.image_col = image_col
        self.target_cols = target_cols or []
        self.transform = transform
        self.image_ext = image_ext

        if not self.image_dir.exists():
            raise FileNotFoundError(f"Image directory not found: {self.image_dir}")

        if image_col not in data.columns:
            raise ValueError(f"Column '{image_col}' not found in data. Available: {list(data.columns)}")

        if target_cols:
            missing_cols = [col for col in target_cols if col not in data.columns]
            if missing_cols:
                raise ValueError(f"Target columns not found in data: {missing_cols}")

        logger.info(f"Initialized {self.__class__.__name__} with {len(self)} samples")
        if target_cols:
            logger.info(f"  Target columns: {target_cols}")

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> Union[Any, Tuple[Any, Any]]:
        image_id = self.data.iloc[idx][self.image_col]
        image_path = self.image_dir / f"{image_id}{self.image_ext}"

        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_path}")

        try:
            image = Image.open(image_path).convert('RGB')
        except Exception as e:
            raise IOError(f"Error loading image {image_path}: {e}")

        if self.transform:
            image = self.transform(image)

        if self.target_cols:
            targets = self.data.iloc[idx][self.target_cols].values.astype('float32')
            targets = torch.tensor(targets)
            return image, targets

        return image


class ImagePathDataset(_Dataset):
    """
    Dataset that loads images from a list of paths.

    Useful for inference when you have direct image paths rather than a DataFrame.
    """

    def __init__(
        self,
        image_paths: List[Union[str, Path]],
        transform: Optional[Callable] = None
    ):
        self.image_paths = [Path(p) for p in image_paths]
        self.transform = transform

        missing_paths = [p for p in self.image_paths if not p.exists()]
        if missing_paths:
            raise FileNotFoundError(
                f"Found {len(missing_paths)} missing image files. "
                f"First few: {missing_paths[:5]}"
            )

        logger.info(f"Initialized {self.__class__.__name__} with {len(self)} images")

    def __len__(self) -> int:
        return len(self.image_paths)

    def __getitem__(self, idx: int) -> Any:
        image_path = self.image_paths[idx]

        try:
            image = Image.open(image_path).convert('RGB')
        except Exception as e:
            raise IOError(f"Error loading image {image_path}: {e}")

        if self.transform:
            image = self.transform(image)

        return image