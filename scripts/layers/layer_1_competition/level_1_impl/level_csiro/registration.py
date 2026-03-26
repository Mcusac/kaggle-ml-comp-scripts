"""CSIRO contest side effects: model id map and ContestRegistry registration."""

from layers.layer_0_core.level_1 import set_model_id_map
from layers.layer_1_competition.level_0_infra.level_1.cli_handlers_dispatch import (
    register_cli_handlers_module,
)
from layers.layer_1_competition.level_0_infra.level_1.notebook import register_notebook_commands_module
from layers.layer_1_competition.level_0_infra.level_1.registry import register_contest

from .level_0.aggregate import aggregate_train_csv
from .level_0.config import CSIROConfig
from .level_0.data_schema import CSIRODataSchema
from .level_0.model_constants import MODEL_ID_MAP
from .level_0.paths import CSIROPaths
from .level_1.post_processor import CSIROPostProcessor

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
