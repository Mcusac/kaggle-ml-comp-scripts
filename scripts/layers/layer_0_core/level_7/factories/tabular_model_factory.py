"""Tabular model factory. Uses level_5, level_6."""

from level_5 import BaseTabularModel
from level_6 import (
    LightGBMModel,
    LogisticRegressionModel,
    MLPModel,
    RidgeModel,
    XGBoostModel,
)


def create_tabular_model(
    model_type: str,
    input_dim: int,
    output_dim: int,
    **kwargs
) -> BaseTabularModel:
    """
    Create a tabular model instance.

    Args:
        model_type: Type of model ('logistic', 'ridge', 'xgboost', 'lgbm', 'mlp').
        input_dim: Input feature dimension.
        output_dim: Output dimension (number of targets).
        **kwargs: Model-specific parameters.

    Returns:
        Model instance.

    Raises:
        ValueError: If model_type is unknown.
    """
    model_type = model_type.lower()

    if model_type in ['logistic', 'logistic_regression', 'lr']:
        return LogisticRegressionModel(**kwargs)

    elif model_type in ['ridge']:
        return RidgeModel(**kwargs)

    elif model_type in ['xgboost', 'xgb']:
        return XGBoostModel(**kwargs)

    elif model_type in ['lgbm', 'lightgbm']:
        return LightGBMModel(**kwargs)

    elif model_type in ['mlp', 'neural_network', 'nn']:
        return MLPModel(
            input_dim=input_dim,
            output_dim=output_dim,
            **kwargs
        )

    else:
        raise ValueError(
            f"Unknown model type: {model_type}. "
            f"Must be one of: 'logistic', 'ridge', 'xgboost', 'lgbm', 'mlp'"
        )
