"""Tabular model base class and PyTorch datasets for dense and sparse label spaces."""

from .base import BaseTabularModel
from .sparse_tabular_dataset import SparseTabularDataset

__all__ = [
    "BaseTabularModel",
    "SparseTabularDataset",
]