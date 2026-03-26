"""Transform mode for vision (TRAIN, VAL, TEST, TTA)."""

from enum import Enum


class TransformMode(Enum):
    """
    Enumeration of transform application modes.

    - TRAIN: Random/probabilistic augmentation for training
    - VAL: No augmentation, preprocessing only for validation
    - TEST: Same as VAL, but semantically for test data
    - TTA: Deterministic variants for test-time augmentation
    """
    TRAIN = "train"
    VAL = "val"
    TEST = "test"
    TTA = "tta"