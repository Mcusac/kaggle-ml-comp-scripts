"""None-value guard."""

from typing import Any

from level_0 import DataValidationError


def check_not_none(value: Any, name: str = "value") -> None:
    """
    Ensure a value is not None.

    Args:
        value: Value to check
        name: Name used in error message

    Raises:
        DataValidationError: If value is None
    """
    if value is None:
        raise DataValidationError(f"{name} cannot be None")