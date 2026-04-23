"""Streaming datasets; load_jpg via PIL; target_cols provided by contest."""

import random
import pandas as pd

from pathlib import Path
from typing import Callable, Iterator, List, Optional
from torchvision.transforms import ToTensor

from layers.layer_0_core.level_0 import get_logger, load_image_pil, get_torch

_torch = get_torch()
IterableDataset = _torch.utils.data.IterableDataset if _torch else object
_logger = get_logger(__name__)


class BaseStreamingDataset(IterableDataset):
    """Base streaming dataset; target_cols from contest primary_targets."""

    def __init__(
        self,
        data: pd.DataFrame,
        data_root: str,
        transform: Optional[Callable] = None,
        target_cols: Optional[List[str]] = None,
        shuffle: bool = False,
        image_path_column: str = 'image_path',
    ):
        self.data_rows = data.reset_index(drop=True).to_dict('records')
        self.data_root = Path(data_root)
        self.transform = transform
        self.shuffle = shuffle
        self.image_path_column = image_path_column
        self.target_cols = target_cols or []
        if self.data_rows and self.target_cols:
            req = [image_path_column] + self.target_cols
            missing = [c for c in req if c not in self.data_rows[0]]
            if missing:
                raise ValueError(f"Missing columns: {missing}")
        self._length = len(self.data_rows)

    def __len__(self) -> int:
        return self._length

    def __iter__(self) -> Iterator:
        torch = get_torch()
        worker_info = torch.utils.data.get_worker_info()
        indices = list(range(len(self.data_rows)))
        if self.shuffle:
            random.shuffle(indices)
        if worker_info is None:
            for i in indices:
                yield self._load_item(i)
        else:
            nw, wid = worker_info.num_workers, worker_info.id
            for i in indices[wid::nw]:
                yield self._load_item(i)

    def _load_item(self, idx: int):
        raise NotImplementedError

    def _load_image(self, path: Path):
        return load_image_pil(path)

    def _get_targets(self, row: dict):
        torch = get_torch()
        return torch.tensor([float(row[c]) for c in self.target_cols], dtype=torch.float32)


class StreamingDataset(BaseStreamingDataset):
    """Full image; returns (image_tensor, targets_tensor)."""

    def _load_item(self, idx: int):
        torch = get_torch()
        row = self.data_rows[idx]
        path = self.data_root / row[self.image_path_column]
        img = self._load_image(path)
        if self.transform:
            img = self.transform(img)
        else:
            img = ToTensor()(img)
        t = self._get_targets(row) if self.target_cols else torch.zeros(0, dtype=torch.float32)
        return img, t


class StreamingSplitDataset(BaseStreamingDataset):
    """Left/right split; returns (left_tensor, right_tensor, targets_tensor)."""

    def _load_item(self, idx: int):
        torch = get_torch()
        row = self.data_rows[idx]
        path = self.data_root / row[self.image_path_column]
        img = self._load_image(path)
        w, h = img.size
        mid = w // 2
        left = img.crop((0, 0, mid, h))
        right = img.crop((mid, 0, w, h))
        if self.transform:
            left = self.transform(left)
            right = self.transform(right)
        else:
            t = ToTensor()
            left, right = t(left), t(right)
        tgt = self._get_targets(row) if self.target_cols else torch.zeros(0, dtype=torch.float32)
        return left, right, tgt
