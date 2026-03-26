"""CSIRO biomass models."""

from layers.layer_0_core.level_3 import (
    HistGradientBoostingRegressorModel,
    GradientBoostingRegressorModel,
    CatBoostRegressorModel,
    LGBMRegressorModel,
    XGBoostRegressorModel,
    RidgeRegressorModel,
)

from layers.layer_0_core.level_0 import NonNegativePredictionMixin


class BiomassHistGBModel(
    NonNegativePredictionMixin,
    HistGradientBoostingRegressorModel,
):
    pass


class BiomassGBModel(
    NonNegativePredictionMixin,
    GradientBoostingRegressorModel,
):
    pass


class BiomassCatBoostModel(
    NonNegativePredictionMixin,
    CatBoostRegressorModel,
):
    pass


class BiomassLGBMModel(
    NonNegativePredictionMixin,
    LGBMRegressorModel,
):
    pass


class BiomassXGBModel(
    NonNegativePredictionMixin,
    XGBoostRegressorModel,
):
    pass


class BiomassRidgeModel(
    NonNegativePredictionMixin,
    RidgeRegressorModel,
):
    pass