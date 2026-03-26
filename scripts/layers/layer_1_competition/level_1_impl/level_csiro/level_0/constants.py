"""CSIRO regression model type constants."""

CSIRO_REGRESSION_MODEL_TYPES = frozenset({"lgbm", "xgboost", "ridge"})


def validate_regression_model_type(model_type: str) -> None:
    """Raise ValueError if model_type not in CSIRO_REGRESSION_MODEL_TYPES."""
    if model_type not in CSIRO_REGRESSION_MODEL_TYPES:
        raise ValueError(
            f"Invalid regression model type: {model_type}. "
            f"Must be one of: {CSIRO_REGRESSION_MODEL_TYPES}"
        )
