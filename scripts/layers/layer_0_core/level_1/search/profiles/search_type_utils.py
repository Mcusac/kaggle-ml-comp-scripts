"""Search type normalization and validation."""

from layers.layer_0_core.level_0 import VALID_HYPERPARAMETER_SEARCH_TYPES


def normalize_search_type(value: str) -> str:
    """
    Normalize and validate a hyperparameter search type string.
    Raises ValueError if value is not a supported search type.
    """
    normalized = (value or "").strip()
    if normalized not in VALID_HYPERPARAMETER_SEARCH_TYPES:
        raise ValueError(
            f"Unknown search_type: {value!r}. "
            f"Must be one of: {', '.join(sorted(VALID_HYPERPARAMETER_SEARCH_TYPES))}"
        )
    return normalized