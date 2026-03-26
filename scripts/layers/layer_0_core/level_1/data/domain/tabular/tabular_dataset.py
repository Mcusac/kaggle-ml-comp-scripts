"""PyTorch Dataset for dense tabular data. Used by MLP and other tabular NN models."""

import numpy as np

from typing import Optional, Tuple

from layers.layer_0_core.level_0 import get_torch

torch = get_torch()
_Dataset = torch.utils.data.Dataset if torch is not None else object


class TabularDataset(_Dataset):
    """PyTorch Dataset for tabular data."""

    def __init__(self, X: np.ndarray, y: Optional[np.ndarray] = None):
        """
        Initialize dataset.

        Args:
            X: Feature matrix of shape (n_samples, n_features).
            y: Optional target matrix of shape (n_samples, n_targets).
        """
        self.X = torch.FloatTensor(X)
        self.y = torch.FloatTensor(y) if y is not None else None

    def __len__(self) -> int:
        return len(self.X)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, Optional[torch.Tensor]]:
        if self.y is not None:
            return self.X[idx], self.y[idx]
        return self.X[idx], None
