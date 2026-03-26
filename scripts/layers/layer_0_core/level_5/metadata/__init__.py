"""Metadata directory path resolution for Kaggle and local mimic environments."""

from .paths import (
    find_metadata_dir,
    get_writable_metadata_dir,
    load_combo_metadata,
)

__all__ = [
    "find_metadata_dir",
    "get_writable_metadata_dir",
    "load_combo_metadata",
]