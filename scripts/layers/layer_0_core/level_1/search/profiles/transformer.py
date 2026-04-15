"""Transformer/ViT hyperparameter grid profile."""
from typing import Any, Dict, List

from layers.layer_0_core.level_0 import build_parameter_grid, resolve_varied_params


def _get_transformer_hyperparameter_defaults() -> Dict[str, Any]:
    """Default training hyperparameters for transformer/ViT models."""
    return {
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


def _get_varied_params_by_search_type() -> Dict[str, Dict[str, List[Any]]]:
    """Varied params per search type for transformer/ViT."""
    return {
        "quick": {
            "learning_rate": [5e-5, 1e-4, 2e-4],
            "batch_size": [8, 16],
            "weight_decay": [0.01, 0.05],
        },
        "in_depth": {
            "learning_rate": [1e-5, 5e-5, 1e-4, 5e-4, 1e-3, 5e-3, 1e-2],
            "batch_size": [8, 16, 32, 64, 128],
            "optimizer": ["AdamW", "Adam", "SGD"],
            "weight_decay": [0, 1e-5, 1e-4, 1e-3],
            "scheduler_factor": [0.1, 0.5, 0.7],
            "scheduler_patience": [3, 5, 7, 10],
        },
        "thorough": {
            "learning_rate": [1e-5, 5e-5, 1e-4, 5e-4, 1e-3, 5e-3],
            "batch_size": [16, 32, 64],
            "optimizer": ["AdamW", "Adam", "SGD"],
            "weight_decay": [0, 1e-5, 1e-4, 1e-3],
            "loss_function": ["SmoothL1Loss", "MSELoss"],
            "scheduler": ["ReduceLROnPlateau", "CosineAnnealingLR"],
            "scheduler_factor": [0.1, 0.5, 0.7],
            "scheduler_patience": [3, 5, 7, 10],
            "early_stopping_patience": [5, 10, 15],
            "num_epochs": [50, 100, 150],
        },
    }


def get_transformer_hyperparameter_grid(search_type: str = "quick") -> Dict[str, List[Any]]:
    """
    Transformer/ViT hyperparameter grid for grid search.

    Args:
        search_type: 'defaults', 'quick', 'in_depth', 'thorough',
                    'focused_in_depth', or 'focused_thorough'

    Returns:
        Dict mapping hyperparameter names to lists of values.
        All 10 parameters are always included.

    Raises:
        ValueError: For focused_* search types (use get_focused_parameter_grid)
    """
    return build_parameter_grid(
        _get_transformer_hyperparameter_defaults(),
        resolve_varied_params(search_type, _get_varied_params_by_search_type()),
    )