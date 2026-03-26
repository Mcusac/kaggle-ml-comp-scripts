"""Pickle module alias for CSIRO models saved under the 'modeling' namespace.

Models were originally pickled with references to ``modeling.*``. This shim
provides a module object that satisfies those lookups when unpickling.

**Intentional compatibility layer:** Keep this module until saved checkpoints are
re-exported or re-saved under stable import paths. Scope is limited to CSIRO
biomass model classes registered on ``csiro_modeling`` and nested ``models.biomass``.
"""

import types

from layers.layer_0_core.level_0 import NonNegativePredictionMixin

from layers.layer_1_competition.level_1_impl.level_csiro.level_0 import (
    BiomassHistGBModel,
    BiomassGBModel,
    BiomassCatBoostModel,
    BiomassLGBMModel,
    BiomassXGBModel,
    BiomassRidgeModel,
)

csiro_modeling = types.ModuleType("modeling")
csiro_modeling.NonNegativePredictionMixin = NonNegativePredictionMixin
csiro_modeling.BiomassHistGBModel = BiomassHistGBModel
csiro_modeling.BiomassGBModel = BiomassGBModel
csiro_modeling.BiomassCatBoostModel = BiomassCatBoostModel
csiro_modeling.BiomassLGBMModel = BiomassLGBMModel
csiro_modeling.BiomassXGBModel = BiomassXGBModel
csiro_modeling.BiomassRidgeModel = BiomassRidgeModel

models = types.ModuleType("models")
models.biomass = types.ModuleType("biomass")
models.biomass.BiomassHistGBModel = BiomassHistGBModel
models.biomass.BiomassGBModel = BiomassGBModel
models.biomass.BiomassCatBoostModel = BiomassCatBoostModel
models.biomass.BiomassLGBMModel = BiomassLGBMModel
models.biomass.BiomassXGBModel = BiomassXGBModel
models.biomass.BiomassRidgeModel = BiomassRidgeModel
models.biomass.NonNegativePredictionMixin = NonNegativePredictionMixin

csiro_modeling.models = models
