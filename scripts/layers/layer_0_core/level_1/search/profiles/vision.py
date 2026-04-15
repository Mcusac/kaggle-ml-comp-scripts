"""Vision model hyperparameter grid profile."""

from typing import Any, Dict, List

from layers.layer_0_core.level_0 import build_parameter_grid, resolve_varied_params


_DEFAULTS: Dict[str, Any] = {
    "learning_rate": 1e-3,
    "batch_size": 32,
    "weight_decay": 0.01,
}

_VARIED_BY_SEARCH_TYPE: Dict[str, Dict[str, List[Any]]] = {
    "quick": {
        "learning_rate": [5e-4, 1e-3, 2e-3],
        "batch_size": [16, 32],
        "weight_decay": [0.01, 0.05],
    },
    "in_depth": {
        "learning_rate": [1e-4, 5e-4, 1e-3, 5e-3],
        "batch_size": [16, 32, 64],
        "weight_decay": [1e-4, 1e-3, 0.01, 0.05],
    },
    "thorough": {
        "learning_rate": [1e-4, 5e-4, 1e-3, 5e-3, 1e-2],
        "batch_size": [16, 32, 64, 128],
        "weight_decay": [0, 1e-4, 1e-3, 0.01, 0.05],
    },
}


def get_vision_grid(search_type: str = "quick") -> Dict[str, List[Any]]:
    """
    Return a vision hyperparameter grid for the given search intensity.

    Args:
        search_type: One of 'defaults', 'quick', 'in_depth', 'thorough'.

    Returns:
        Dict mapping each hyperparameter name to a list of values to search.
        When search_type is 'defaults', each parameter maps to a single-item
        list containing only its default value.

    Raises:
        ValueError: If search_type is not recognised.
    """
    return build_parameter_grid(
        _DEFAULTS,
        resolve_varied_params(search_type, _VARIED_BY_SEARCH_TYPE),
    )