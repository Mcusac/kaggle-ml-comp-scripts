"""Platform detection utilities (e.g. Kaggle vs local)."""

import os
from pathlib import Path
from typing import Union


def is_kaggle() -> bool:
    """Return True if running in Kaggle environment (kernel env var)."""
    return bool(os.environ.get("KAGGLE_KERNEL_RUN_TYPE", "").strip())


def is_kaggle_input(path: Union[Path, str]) -> bool:
    """Return True if *path* string is under the Kaggle read-only input mount."""
    return str(path).startswith("/kaggle/input")
