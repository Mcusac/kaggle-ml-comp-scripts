"""Command handlers for CLI routing (thin router over per-command modules)."""

import argparse

from typing import Any, Callable, Dict

from layers.layer_0_core.level_0 import Command

from layers.layer_1_competition.level_0_infra.level_0.ensemble import (
    make_handler as make_ensemble,
)
from layers.layer_1_competition.level_0_infra.level_1.commands.cross_validate import (
    make_handler as make_cross_validate,
)
from layers.layer_1_competition.level_0_infra.level_1.commands.export_model import (
    make_handler as make_export,
)
from layers.layer_1_competition.level_0_infra.level_1.commands.grid_search import (
    make_handler as make_grid_search,
)
from layers.layer_1_competition.level_0_infra.level_1.commands.test import (
    make_handler as make_test,
)
from layers.layer_1_competition.level_0_infra.level_1.commands.train import (
    make_handler as make_train,
)
from layers.layer_1_competition.level_0_infra.level_1.commands.train_test import (
    make_handler as make_train_test,
)


def get_command_handlers(builder: Any) -> Dict[str, Callable[[argparse.Namespace], None]]:
    """
    Return framework command handlers that use the injected context builder.
    Call from scripts/run.py with builder from run_helpers.get_handler_context_builder(contest_name).
    """
    return {
        Command.TRAIN.value: make_train(builder),
        Command.TEST.value: make_test(builder),
        Command.TRAIN_TEST.value: make_train_test(builder),
        Command.GRID_SEARCH.value: make_grid_search(builder),
        Command.CROSS_VALIDATE.value: make_cross_validate(builder),
        Command.ENSEMBLE.value: make_ensemble(builder),
        Command.EXPORT_MODEL.value: make_export(builder),
    }
