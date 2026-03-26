"""CSIRO regression model factory."""

from layers.layer_1_competition.level_1_impl.level_csiro.level_0 import (
    BiomassHistGBModel,
    BiomassGBModel,
    BiomassCatBoostModel,
    BiomassLGBMModel,
    BiomassXGBModel,
    BiomassRidgeModel,
)


def create_biomass_model(model_type: str, **params):

    if model_type == "hist_gb":
        return BiomassHistGBModel(**params)

    if model_type == "gb":
        return BiomassGBModel(**params)

    if model_type == "catboost":
        return BiomassCatBoostModel(**params)

    if model_type == "lgbm":
        return BiomassLGBMModel(**params)

    if model_type in ("xgb", "xgboost"):
        return BiomassXGBModel(**params)

    if model_type == "ridge":
        return BiomassRidgeModel(**params)

    raise ValueError(model_type)