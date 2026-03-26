"""IO utilities for loading and saving data.

Provides consistent, validated loading/saving across common data formats.
Depends on level_0 (errors, logging, paths), level_2 (validate_dataframe),
and level_3 (validate_path_is_file).

Example:
    >>> from level_4 import load_csv, load_image, save_json
    >>> df = load_csv('data.csv', required_cols=['id', 'value'])
"""

from .csv import load_csv_raw, load_csv, save_csv
from .images import load_image_raw, load_image, save_image
from .json import load_json_raw, load_json, save_json
from .memmap import (
    should_use_memmap,
    create_memmap,
    load_memmap,
    save_memmap_with_metadata,
    load_memmap_with_metadata,
    MEMMAP_THRESHOLD_MB,
)
from .pickle import (
    PICKLE_HIGHEST_PROTOCOL,
    load_pickle_raw,
    load_pickle,
    save_pickle,
)
from .yaml import load_yaml_raw, load_yaml, save_yaml

__all__ = [
    # CSV
    "load_csv_raw",
    "load_csv",
    "save_csv",
    # Images
    "load_image_raw",
    "load_image",
    "save_image",
    # JSON
    "load_json_raw",
    "load_json",
    "save_json",
    # Memmap
    "should_use_memmap",
    "create_memmap",
    "load_memmap",
    "save_memmap_with_metadata",
    "load_memmap_with_metadata",
    "MEMMAP_THRESHOLD_MB",
    # Pickle
    "PICKLE_HIGHEST_PROTOCOL",
    "load_pickle_raw",
    "load_pickle",
    "save_pickle",
    # YAML
    "load_yaml_raw",
    "load_yaml",
    "save_yaml",
    ]