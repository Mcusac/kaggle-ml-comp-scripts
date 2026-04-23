"""Lazy imports for sklearn and boosting components."""

from typing import Any, Callable, Dict, Tuple

from layers.layer_0_core.level_1 import lazy_import


_SKLEARN_REGISTRY: Dict[str, Tuple[str, str, str, str]] = {
    # function_name: (module, class_name, package, warn_msg)
    "get_standard_scaler": ("sklearn.preprocessing", "StandardScaler", "sklearn", "StandardScaler disabled"),
    "get_pca": ("sklearn.decomposition", "PCA", "sklearn", "PCA disabled"),
    "get_pls_regression": ("sklearn.cross_decomposition", "PLSRegression", "sklearn", "PLSRegression disabled"),
    "get_gaussian_mixture": ("sklearn.mixture", "GaussianMixture", "sklearn", "GaussianMixture disabled"),
    "get_gradient_boosting_regressor": ("sklearn.ensemble", "GradientBoostingRegressor", "sklearn", "GradientBoostingRegressor disabled"),
    "get_hist_gradient_boosting_regressor": ("sklearn.ensemble", "HistGradientBoostingRegressor", "sklearn", "HistGradientBoostingRegressor disabled"),
    "get_random_forest_regressor": ("sklearn.ensemble", "RandomForestRegressor", "sklearn", "RandomForestRegressor disabled"),
    "get_catboost": ("catboost", "CatBoostRegressor", "catboost", "CatBoost disabled"),
    "get_lightgbm": ("lightgbm", "LGBMRegressor", "lightgbm", "LightGBM disabled"),
    "get_lgbm_classifier": ("lightgbm", "LGBMClassifier", "lightgbm", "LGBMClassifier disabled"),
    "get_xgboost": ("xgboost", "XGBRegressor", "xgboost", "XGBoost disabled"),
    "get_xgb_classifier": ("xgboost", "XGBClassifier", "xgboost", "XGBClassifier disabled"),
    "get_ridge": ("sklearn.linear_model", "Ridge", "sklearn", "Ridge regression disabled"),
    "get_logistic_regression": ("sklearn.linear_model", "LogisticRegression", "sklearn", "LogisticRegression disabled"),
    "get_ridge_classifier": ("sklearn.linear_model", "RidgeClassifier", "sklearn", "RidgeClassifier disabled"),
    "get_linear_regression": ("sklearn.linear_model", "LinearRegression", "sklearn", "LinearRegression disabled"),
    "get_lasso": ("sklearn.linear_model", "Lasso", "sklearn", "Lasso regression disabled"),
    "get_elastic_net": ("sklearn.linear_model", "ElasticNet", "sklearn", "ElasticNet disabled"),
    "get_kfold": ("sklearn.model_selection", "KFold", "sklearn", "KFold disabled"),
    "get_stratified_kfold": ("sklearn.model_selection", "StratifiedKFold", "sklearn", "StratifiedKFold disabled"),
    "get_train_test_split": ("sklearn.model_selection", "train_test_split", "sklearn", "train_test_split disabled"),
    "get_cross_val_score": ("sklearn.model_selection", "cross_val_score", "sklearn", "cross_val_score disabled"),
}


def _make_loader(module: str, cls: str, package: str, warn: str) -> Callable[[], Any]:
    def _loader():
        return lazy_import(module, cls, package=package, warn=warn)
    return _loader


def _get(name: str) -> Callable[[], Any]:
    module, cls, package, warn = _SKLEARN_REGISTRY[name]
    return _make_loader(module, cls, package, warn)


def __getattr__(name: str) -> Any:
    if name in _SKLEARN_REGISTRY:
        module, cls, package, warn = _SKLEARN_REGISTRY[name]
        return _make_loader(module, cls, package, warn)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


get_standard_scaler = _get("get_standard_scaler")
get_pca = _get("get_pca")
get_pls_regression = _get("get_pls_regression")
get_gaussian_mixture = _get("get_gaussian_mixture")
get_gradient_boosting_regressor = _get("get_gradient_boosting_regressor")
get_hist_gradient_boosting_regressor = _get("get_hist_gradient_boosting_regressor")
get_random_forest_regressor = _get("get_random_forest_regressor")
get_catboost = _get("get_catboost")
get_lightgbm = _get("get_lightgbm")
get_lgbm_classifier = _get("get_lgbm_classifier")
get_xgboost = _get("get_xgboost")
get_xgb_classifier = _get("get_xgb_classifier")
get_ridge = _get("get_ridge")
get_logistic_regression = _get("get_logistic_regression")
get_ridge_classifier = _get("get_ridge_classifier")
get_linear_regression = _get("get_linear_regression")
get_lasso = _get("get_lasso")
get_elastic_net = _get("get_elastic_net")
get_kfold = _get("get_kfold")
get_stratified_kfold = _get("get_stratified_kfold")
get_train_test_split = _get("get_train_test_split")
get_cross_val_score = _get("get_cross_val_score")
