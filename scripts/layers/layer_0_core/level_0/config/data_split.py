"""Universal ML data partition labels."""

from enum import Enum


class DataSplit(Enum):
    """Universal ML data partition labels."""

    TRAIN = "train"
    VAL = "val"
    TEST = "test"
