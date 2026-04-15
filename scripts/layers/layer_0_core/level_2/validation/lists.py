"""List validation.

Validation utilities for lists and collections.
"""

from typing import Iterable, Collection, Any

from layers.layer_0_core.level_0 import DataValidationError
from layers.layer_0_core.level_1 import check_not_none

def validate_list(
    values: Iterable[Any],
    allowed: Collection[Any],
    name: str = "value"
) -> None:
    """
    Validate that all values in a list are in the set of allowed values.
    
    Args:
        values: List of values to validate
        allowed: Collection of allowed values
        name: Name of the values for error messages
        
    Raises:
        DataValidationError: If any value is not in the allowed set
        
    Example:
        >>> validate_list(['red', 'blue'], ['red', 'blue', 'green'], "color")
        >>> validate_list([1, 2], [1, 2, 3, 4, 5], "ID")
    """
    invalid_values = [v for v in values if v not in allowed]
    if invalid_values:
        raise DataValidationError(
            f"Invalid {name}(s): {invalid_values}. "
            f"Allowed: {sorted(allowed)}"
        )


def validate_list_not_empty(
    values: Collection[Any],
    name: str = "list"
) -> None:
    """
    Validate that a list/collection is not None and not empty.
    
    Args:
        values: Collection to validate
        name: Name of the collection for error messages
        
    Raises:
        DataValidationError: If collection is None or empty
        
    Example:
        >>> validate_list_not_empty([1, 2, 3], "items")
        >>> validate_list_not_empty(my_list, "required fields")
    """
    check_not_none(values, name)
    
    if len(values) == 0:
        raise DataValidationError(f"{name} cannot be empty")