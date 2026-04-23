"""Auto-generated package exports."""


from .oom_retry import handle_oom_error_with_retry

from .sklearn_models import (
    CatBoostRegressorModel,
    GradientBoostingRegressorModel,
    HistGradientBoostingRegressorModel,
    LGBMRegressorModel,
    RidgeRegressorModel,
    XGBoostRegressorModel,
    create_regression_model,
)

from .timm_model import (
    DEFAULT_IMAGE_SIZE,
    DatasetType,
    TimmModel,
)

from .tta_predictor import TTAPredictor

__all__ = [
    "CatBoostRegressorModel",
    "DEFAULT_IMAGE_SIZE",
    "DatasetType",
    "GradientBoostingRegressorModel",
    "HistGradientBoostingRegressorModel",
    "LGBMRegressorModel",
    "RidgeRegressorModel",
    "TTAPredictor",
    "TimmModel",
    "XGBoostRegressorModel",
    "create_regression_model",
    "handle_oom_error_with_retry",
]
