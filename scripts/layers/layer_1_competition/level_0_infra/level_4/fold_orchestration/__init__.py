"""Fold orchestration — coordinates trainer and dataloader creation for a single CV fold."""

from .single_fold import train_single_fold

__all__ = ["train_single_fold"]
