"""Register the `rna3d` contest with ContestRegistry on package import."""

from layers.layer_1_competition.level_0_infra.level_1 import (
    register_contest,
    register_notebook_commands_module,
)
from layers.layer_1_competition.level_0_infra.level_2 import register_cli_handlers_module

from layers.layer_1_competition.level_1_impl.level_rna3d.level_0 import (
    RNA3DConfig,
    RNA3DDataSchema,
    RNA3DPaths,
    RNA3DPostProcessor,
)

register_contest(
    "rna3d",
    RNA3DConfig,
    RNA3DDataSchema,
    RNA3DPaths,
    RNA3DPostProcessor,
)

register_notebook_commands_module(
    "rna3d",
    "layers.layer_1_competition.level_1_impl.level_rna3d.level_0.notebook_commands",
)

register_cli_handlers_module(
    "rna3d",
    "layers.layer_1_competition.level_1_impl.level_rna3d.level_4.handlers",
)
