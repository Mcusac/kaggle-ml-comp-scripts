"""General training hyperparameter grid profile."""

from typing import Any, Dict, List

from layers.layer_0_core.level_0 import build_parameter_grid, resolve_varied_params


_DEFAULTS: Dict[str, Any] = {
    "learning_rate": 1e-3,
    "batch_size": 32,
    "optimizer": "AdamW",
    "weight_decay": 1e-4,
    "loss_function": "SmoothL1Loss",
    "scheduler": "ReduceLROnPlateau",
    "scheduler_factor": 0.5,
    "scheduler_patience": 5,
    "early_stopping_patience": 10,
    "num_epochs": 100,
}

_VARIED_BY_SEARCH_TYPE: Dict[str, Dict[str, List[Any]]] = {
    "quick": {
        "learning_rate": [1e-3, 5e-4],
        "batch_size": [32, 64],
    },
    "in_depth": {
        "learning_rate": [1e-3, 5e-4, 1e-4],
        "batch_size": [32, 64, 128],
        "optimizer": ["AdamW", "Adam"],
        "weight_decay": [1e-4, 1e-3],
        "num_epochs": [100, 150],
    },
    "thorough": {
        "learning_rate": [1e-3, 5e-4, 1e-4, 5e-5],
        "batch_size": [16, 32, 64, 128],
        "optimizer": ["AdamW", "Adam", "SGD"],
        "weight_decay": [1e-5, 1e-4, 1e-3],
        "num_epochs": [100, 150, 200],
    },
}


def get_training_grid(search_type: str = "defaults") -> Dict[str, List[Any]]:
    """
    Return a training hyperparameter grid for the given search intensity.

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