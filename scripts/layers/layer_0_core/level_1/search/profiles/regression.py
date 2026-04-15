"""Regression model hyperparameter grid profiles."""

from typing import Any, Dict, List

from layers.layer_0_core.level_0 import build_parameter_grid, resolve_varied_params


# Maps the canonical model type name to its default hyperparameters.
# Add new model types here; no function changes required.
_DEFAULTS: Dict[str, Dict[str, Any]] = {
    "lgbm": {
        "n_estimators": 300,
        "learning_rate": 0.05,
        "num_leaves": 31,
        "max_depth": -1,
        "min_child_samples": 20,
        "subsample": 1.0,
        "colsample_bytree": 1.0,
        "random_state": 42,
    },
    "xgboost": {
        "n_estimators": 300,
        "learning_rate": 0.05,
        "max_depth": 6,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "gamma": 0,
        "reg_alpha": 0,
        "reg_lambda": 1,
        "random_state": 42,
    },
    "ridge": {
        "alpha": 1.0,
        "fit_intercept": True,
        "copy_X": True,
        "max_iter": None,
        "tol": 1e-4,
        "solver": "auto",
        "positive": False,
        "random_state": 42,
    },
}

# Accepted aliases → canonical model type name.
# Alias resolution happens before any dict lookup so all downstream
# logic operates only on canonical names.
_MODEL_TYPE_ALIASES: Dict[str, str] = {
    "xgb": "xgboost",
}

_VARIED_BY_SEARCH_TYPE: Dict[str, Dict[str, Dict[str, List[Any]]]] = {
    "quick": {
        "lgbm": {
            "n_estimators": [100, 300],
            "learning_rate": [0.01, 0.05],
        },
        "xgboost": {
            "n_estimators": [100, 300],
            "learning_rate": [0.01, 0.05],
        },
        "ridge": {
            "alpha": [0.1, 1.0, 10.0],
        },
    },
    "in_depth": {
        "lgbm": {
            "n_estimators": [100, 300, 500],
            "learning_rate": [0.01, 0.05, 0.1],
            "num_leaves": [15, 31, 63],
        },
        "xgboost": {
            "n_estimators": [100, 300, 500],
            "learning_rate": [0.01, 0.05, 0.1],
            "max_depth": [4, 6, 8],
        },
        "ridge": {
            "alpha": [0.01, 0.1, 1.0, 10.0],
            "fit_intercept": [True, False],
        },
    },
}


def get_regression_grid(
    model_type: str,
    search_type: str = "quick",
) -> Dict[str, List[Any]]:
    """
    Return a regression hyperparameter grid for the given model and search intensity.

    Args:
        model_type: One of 'lgbm', 'xgboost' (or alias 'xgb'), 'ridge'.
        search_type: One of 'defaults', 'quick', 'in_depth'.

    Returns:
        Dict mapping each hyperparameter name to a list of values to search.
        When search_type is 'defaults', each parameter maps to a single-item
        list containing only its default value.

    Raises:
        ValueError: If model_type or search_type is not recognised.
    """
    resolved_type = _MODEL_TYPE_ALIASES.get(model_type, model_type)

    if resolved_type not in _DEFAULTS:
        valid_models = ", ".join(f"'{m}'" for m in _DEFAULTS)
        raise ValueError(
            f"Unknown model_type: '{model_type}'. Must be one of {valid_models}."
        )

    defaults = _DEFAULTS[resolved_type]
    varied_by_model = resolve_varied_params(search_type, _VARIED_BY_SEARCH_TYPE)
    varied = varied_by_model.get(resolved_type, {})

    return build_parameter_grid(defaults, varied)