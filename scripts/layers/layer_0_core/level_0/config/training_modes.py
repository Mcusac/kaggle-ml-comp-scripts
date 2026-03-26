"""Training modes for tabular models."""

from enum import Enum


class TrainingMode(Enum):
    """Training mode enumeration."""
    LOAD_OR_TRAIN = 'load_or_train'  # Load if exists, otherwise train
    TRAIN_NEW = 'train_new'  # Always train new model
    LOAD_ONLY = 'load_only'  # Only load, fail if not found