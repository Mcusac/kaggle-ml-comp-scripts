"""
Tabular/sklearn regression models for multi-output regression.

Used for regression heads over tabular or vision-derived features (e.g. CSIRO biomass).
"""

from layers.layer_0_core.level_2 import (
    BaseMultiOutputRegressionModel,
    get_catboost,
    get_gradient_boosting_regressor,
    get_lightgbm,
    get_ridge,
    get_xgboost,
)


class HistGradientBoostingRegressorModel(BaseMultiOutputRegressionModel):
    """HistGradientBoostingRegressor wrapper for regression with multi-output support."""

    def _get_model_class(self):
        _, HistGradientBoostingRegressor = get_gradient_boosting_regressor()
        return HistGradientBoostingRegressor

    def _get_default_params(self):
        return {
            "max_iter": 300,
            "learning_rate": 0.05,
            "max_depth": None,
            "l2_regularization": 0.44,
            "random_state": 42,
        }

    def _get_model_name(self):
        return "hist_gb"


class GradientBoostingRegressorModel(BaseMultiOutputRegressionModel):
    """GradientBoostingRegressor wrapper for regression with multi-output support."""

    def _get_model_class(self):
        GradientBoostingRegressor, _ = get_gradient_boosting_regressor()
        return GradientBoostingRegressor

    def _get_default_params(self):
        return {
            "n_estimators": 1354,
            "learning_rate": 0.010,
            "max_depth": 3,
            "subsample": 0.60,
            "random_state": 42,
        }

    def _get_model_name(self):
        return "gb"


class CatBoostRegressorModel(BaseMultiOutputRegressionModel):
    """CatBoostRegressor wrapper for regression with multi-output support."""

    def _get_model_class(self):
        return get_catboost()

    def _get_default_params(self):
        return {
            "iterations": 1900,
            "learning_rate": 0.045,
            "depth": 4,
            "l2_leaf_reg": 0.56,
            "random_strength": 0.045,
            "bagging_temperature": 0.98,
            "verbose": 0,
            "random_state": 42,
            "allow_writing_files": False,
        }

    def _get_model_name(self):
        return "catboost"


class LGBMRegressorModel(BaseMultiOutputRegressionModel):
    """LGBMRegressor wrapper for regression with multi-output support."""

    def _get_model_class(self):
        return get_lightgbm()

    def _get_default_params(self):
        return {
            "n_estimators": 807,
            "learning_rate": 0.014,
            "num_leaves": 48,
            "min_child_samples": 19,
            "subsample": 0.745,
            "colsample_bytree": 0.745,
            "reg_alpha": 0.21,
            "reg_lambda": 3.78,
            "verbose": -1,
            "random_state": 42,
        }

    def _get_model_name(self):
        return "lgbm"


class XGBoostRegressorModel(BaseMultiOutputRegressionModel):
    """XGBoostRegressor wrapper for regression with multi-output support."""

    def _get_model_class(self):
        return get_xgboost()

    def _get_default_params(self):
        return {
            "n_estimators": 300,
            "learning_rate": 0.05,
            "max_depth": 6,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
            "gamma": 0,
            "reg_alpha": 0,
            "reg_lambda": 1,
            "random_state": 42,
        }

    def _get_model_name(self):
        return "xgboost"


class RidgeRegressorModel(BaseMultiOutputRegressionModel):
    """Ridge regression wrapper for regression with multi-output support."""

    def _get_model_class(self):
        return get_ridge()

    def _get_default_params(self):
        return {
            "alpha": 1.0,
            "fit_intercept": True,
            "copy_X": True,
            "max_iter": None,
            "tol": 1e-4,
            "solver": "auto",
            "positive": False,
            "random_state": 42,
        }

    def _get_model_name(self):
        return "ridge"


def create_regression_model(model_type: str, **params):
    """
    Factory function to create regression models.

    Args:
        model_type: Type of model ('hist_gb', 'gb', 'catboost', 'lgbm', 'xgboost', 'xgb', 'ridge')
        **params: Model-specific parameters

    Returns:
        Model instance
    """
    if model_type == "hist_gb":
        return HistGradientBoostingRegressorModel(**params)
    if model_type == "gb":
        return GradientBoostingRegressorModel(**params)
    if model_type == "catboost":
        return CatBoostRegressorModel(**params)
    if model_type == "lgbm":
        return LGBMRegressorModel(**params)
    if model_type in ("xgboost", "xgb"):
        return XGBoostRegressorModel(**params)
    if model_type == "ridge":
        return RidgeRegressorModel(**params)
    raise ValueError(f"Unknown model type: {model_type}")