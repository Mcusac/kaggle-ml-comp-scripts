"""Register ARC-AGI-2 contest side effects."""

from layers.layer_1_competition.level_0_infra.level_1 import (
    register_contest,
    register_notebook_commands_module,
)
from layers.layer_1_competition.level_0_infra.level_2 import register_cli_handlers_module
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.paths import ARC26Paths
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.config import (
    ARC26Config,
    ARC26DataSchema,
    ARC26PostProcessor,
)

register_contest(
    "arc_agi_2",
    ARC26Config,
    ARC26DataSchema,
    ARC26Paths,
    ARC26PostProcessor,
)

register_notebook_commands_module(
    "arc_agi_2",
    "layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.notebook_commands",
)

register_cli_handlers_module(
    "arc_agi_2",
    "layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_8.handlers",
)

