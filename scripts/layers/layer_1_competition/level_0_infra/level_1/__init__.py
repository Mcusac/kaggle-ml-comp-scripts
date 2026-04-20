"""Competition infra tier 1: feature extraction, export, handlers, paths."""

from . import contest, export, features, paths, pipelines, registry

from .contest import *
from .export import *
from .features import *
from .paths import *
from .pipelines import *
from .registry import *

from layers.layer_0_core.level_0 import PipelineResult
from layers.layer_0_core.level_1.pipelines import (
    run_two_stage_pipeline_result_with_validation_first,
)

from layers.layer_1_competition.level_0_infra.level_0.dispatch import (
    register_notebook_commands_module,
)

from layers.layer_1_competition.level_0_infra.level_2.grid_search.base import (
    ContestGridSearchBase,
)
from layers.layer_1_competition.level_0_infra.level_2.grid_search.context import (
    build_grid_search_context,
)
from layers.layer_1_competition.level_0_infra.level_2.notebook.base_commands import (
    build_run_py_base_command,
)

__all__ = (
    tuple(contest.__all__)
    + tuple(export.__all__)
    + tuple(features.__all__)
    + tuple(paths.__all__)
    + tuple(pipelines.__all__)
    + tuple(registry.__all__)
    + (
        "PipelineResult",
        "run_two_stage_pipeline_result_with_validation_first",
        "register_notebook_commands_module",
        "ContestGridSearchBase",
        "build_grid_search_context",
        "build_run_py_base_command",
    )
)


def __getattr__(name: str):
    if name == "get_command_handlers":
        from layers.layer_1_competition.level_0_infra.level_2.handlers import (
            get_command_handlers,
        )

        return get_command_handlers
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
