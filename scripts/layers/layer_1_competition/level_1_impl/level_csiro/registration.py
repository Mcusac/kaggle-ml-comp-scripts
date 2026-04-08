"""CSIRO contest side effects: model id map and ContestRegistry registration."""

from layers.layer_0_core.level_1 import set_model_id_map

from layers.layer_1_competition.level_0_infra.level_1 import (
    register_contest,
    register_notebook_commands_module,
)
from layers.layer_1_competition.level_0_infra.level_2 import register_cli_handlers_module

from layers.layer_1_competition.level_1_impl.level_csiro.level_0 import (
    aggregate_train_csv,
    CSIROConfig,
    CSIRODataSchema,
    CSIROPaths,
    MODEL_ID_MAP,
)
from layers.layer_1_competition.level_1_impl.level_csiro.level_1 import CSIROPostProcessor

set_model_id_map(MODEL_ID_MAP)

register_contest(
    "csiro",
    CSIROConfig,
    CSIRODataSchema,
    CSIROPaths,
    CSIROPostProcessor,
    training_data_loader=aggregate_train_csv,
)

register_notebook_commands_module(
    "csiro",
    "layers.layer_1_competition.level_1_impl.level_csiro.level_0.notebook_commands",
)

register_cli_handlers_module(
    "csiro",
    "layers.layer_1_competition.level_1_impl.level_csiro.level_7.handlers",
)
