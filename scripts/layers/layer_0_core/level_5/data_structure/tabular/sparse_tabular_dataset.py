"""Sparse dataset for large label spaces in tabular models. Uses level_0 and level_4.load_json."""

import numpy as np

from pathlib import Path
from typing import Union, Optional, Tuple
from scipy.sparse import csr_matrix, issparse, spmatrix

from layers.layer_0_core.level_0 import get_logger, get_torch
from layers.layer_0_core.level_4 import load_json

_logger = get_logger(__name__)

_torch = get_torch()
if _torch is None:
    raise ImportError("torch is required for SparseTabularDataset")

Dataset = _torch.utils.data.Dataset


class SparseTabularDataset(Dataset):
    """
    PyTorch Dataset for sparse multi-label classification.
    
    Keeps labels sparse (scipy CSR format) and extracts rows efficiently.
    Supports memmap for features to save RAM.
    
    Features:
    - Accepts numpy arrays, memmap, or Path to memmap for features
    - Efficient CSR row extraction (no full dense conversion)
    - Memory-efficient for large label spaces (16K+ labels)
    - Supports label smoothing
    """
    
    def __init__(
        self,
        X: Union[np.ndarray, np.memmap, Path, str],
        y: Union[spmatrix, np.ndarray],
        indices: Optional[np.ndarray] = None,
        label_smoothing: float = 0.0
    ):
        """
        Initialize sparse dataset.
        
        Args:
            X: Feature matrix (n_samples, n_features) - numpy array, memmap, or Path to memmap
            y: Label matrix (n_samples, n_labels) - scipy sparse CSR matrix or numpy array
            indices: Optional indices to subset the dataset (for train/val split)
            label_smoothing: Label smoothing factor (0.0 = no smoothing)
        """
        # Handle memmap path - load lazily
        if isinstance(X, (str, Path)):
            self.X_path = Path(X)
            self.X = None  # Load on-demand
        else:
            self.X_path = None
            self.X = X
        
        self.y = y
        
        # Get shape for indices
        if indices is None:
            if self.X_path is not None:
                # Try to get shape from metadata
                metadata_path = self.X_path.with_suffix('.npy.meta')
                if metadata_path.exists():
                    metadata = load_json(str(metadata_path))
                    n_samples = metadata.get('shape', [0])[0]
                else:
                    # Fallback: load just to get shape
                    if isinstance(self.X_path, Path):
                        self.X = np.load(str(self.X_path), mmap_mode='r')
                        n_samples = self.X.shape[0]
                    else:
                        n_samples = 0
                self.indices = np.arange(n_samples)
            else:
                self.indices = np.arange(len(self.X))
        else:
            self.indices = indices
        
        self.y_is_sparse = issparse(y)
        self.n_labels = y.shape[1] if hasattr(y, 'shape') else 0
        self.label_smoothing = label_smoothing
    
    def __len__(self) -> int:
        """Return dataset size."""
        return len(self.indices)
    
    def __getitem__(self, idx: int) -> Tuple[_torch.Tensor, _torch.Tensor]:
        """
        Get a single sample.
        
        Args:
            idx: Index into the dataset
            
        Returns:
            tuple: (features, labels) as torch tensors
        """
        actual_idx = self.indices[idx]
        
        # Load memmap if needed (lazy loading)
        if self.X_path is not None and self.X is None:
            if isinstance(self.X_path, Path):
                self.X = np.load(str(self.X_path), mmap_mode='r')
            else:
                raise ValueError(f"Invalid X_path type: {type(self.X_path)}")
        
        # Get features (from array or memmap - both support indexing)
        features = np.array(self.X[actual_idx], dtype=np.float32)
        
        # Get labels - optimized sparse extraction
        if self.y_is_sparse:
            # Use CSR format's efficient row access
            if isinstance(self.y, csr_matrix):
                # Pre-allocate and fill only non-zero values (faster than getrow().toarray())
                labels = np.zeros(self.n_labels, dtype=np.float32)
                start = self.y.indptr[actual_idx]
                end = self.y.indptr[actual_idx + 1]
                if end > start:
                    labels[self.y.indices[start:end]] = self.y.data[start:end].astype(np.float32)
            else:
                # Fallback for other sparse formats
                labels = self.y.getrow(actual_idx).toarray()[0].astype(np.float32)
        else:
            labels = self.y[actual_idx].astype(np.float32)
        
        # Apply label smoothing if enabled
        # Positive labels (1.0) -> 1.0 - smoothing
        # Negative labels (0.0) -> smoothing / n_labels
        if self.label_smoothing > 0.0:
            # Apply smoothing: positive labels become 1.0 - smoothing, negative become smoothing / n_labels
            labels = labels * (1.0 - self.label_smoothing) + self.label_smoothing / self.n_labels
        
        return _torch.from_numpy(features), _torch.from_numpy(labels)
