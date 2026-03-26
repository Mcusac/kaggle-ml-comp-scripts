"""Search type resolution for hyperparameter grid profiles."""

from typing import Any, Dict, List


def resolve_varied_params(
    search_type: str,
    varied_by_search_type: Dict[str, Dict[str, List[Any]]],
) -> Dict[str, List[Any]]:
    """
    Resolve a search_type string to its varied-parameter dict.

    Returns an empty dict when search_type is 'defaults', causing
    build_parameter_grid to return only the defaults with no variation.

    Raises ValueError for any unknown search_type.
    """
    if search_type == "defaults":
        return {}

    if search_type in varied_by_search_type:
        return varied_by_search_type[search_type]

    valid = ", ".join(f"'{k}'" for k in ["defaults", *varied_by_search_type])
    raise ValueError(
        f"Unknown search_type: '{search_type}'. Must be one of {valid}."
    )