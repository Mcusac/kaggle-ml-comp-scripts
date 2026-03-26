"""Command definitions for CLI routing."""

from enum import Enum


class Command(Enum):
    """Enumeration of valid framework CLI commands."""

    TRAIN = 'train'
    TEST = 'test'
    TRAIN_TEST = 'train_test'
    GRID_SEARCH = 'grid_search'
    CROSS_VALIDATE = 'cross_validate'
    ENSEMBLE = 'ensemble'
    EXPORT_MODEL = 'export_model'
