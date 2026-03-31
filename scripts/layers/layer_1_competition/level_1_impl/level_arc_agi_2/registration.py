"""Register ARC-AGI-2 contest side effects."""

from layers.layer_1_competition.level_0_infra.level_1 import (
    register_cli_handlers_module,
    register_notebook_commands_module,
    register_contest,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    ARC26Config,
    ARC26DataSchema,
    ARC26Paths,
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
    "layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_6.handlers",
)

