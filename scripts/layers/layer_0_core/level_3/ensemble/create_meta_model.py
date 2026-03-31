"""Meta-model factory for stacking ensembles.

Depends on level_2 sklearn loaders — lives at level_3 or higher.
Uses the project-standard lazy loader pattern so sklearn unavailability
produces a controlled warning rather than a raw ImportError.
"""

from typing import Any, Dict, Optional

from layers.layer_0_core.level_2 import get_lasso, get_linear_regression, get_ridge


def create_meta_model(
    meta_model_type: str,
    meta_model_params: Optional[Dict[str, Any]],
    random_state: int,
) -> Any:
    """
    Instantiate a meta-model for stacking ensemble combination.

    Args:
        meta_model_type:   One of 'ridge', 'linear', 'lasso'.
        meta_model_params: Optional hyperparameter overrides.
                           Recognised keys per type:
                             ridge / lasso: 'alpha' (float, default 1.0)
        random_state:      Random seed passed to models that accept it.

    Returns:
        Fitted-ready sklearn estimator instance.

    Raises:
        ValueError:  If meta_model_type is not recognised.
        ImportError: (via lazy loader warning) if sklearn is unavailable.
    """
    alpha = (meta_model_params or {}).get("alpha", 1.0)

    if meta_model_type == "ridge":
        Ridge = get_ridge()
        return Ridge(alpha=alpha, random_state=random_state)

    if meta_model_type == "linear":
        LinearRegression = get_linear_regression()
        return LinearRegression()

    if meta_model_type == "lasso":
        Lasso = get_lasso()
        return Lasso(alpha=alpha, random_state=random_state)

    raise ValueError(
        f"Unknown meta_model_type: '{meta_model_type}'. "
        f"Expected one of: 'ridge', 'linear', 'lasso'."
    )