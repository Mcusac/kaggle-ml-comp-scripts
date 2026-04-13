"""Hyperparameter grid-search command handler."""

import argparse

from typing import Any, Callable

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_9 import HyperparameterGridSearch

from layers.layer_1_competition.level_0_infra.level_0 import setup_handler_context

logger = get_logger(__name__)


def make_handler(builder: Any) -> Callable[[argparse.Namespace], None]:
    def _handle_grid_search(args: argparse.Namespace) -> None:
        _, config, model_type, _, _, _ = setup_handler_context(args=args, builder=builder)
        param_grid = {
            "learning_rate": [1e-3, 1e-4, 1e-5],
            "batch_size": [16, 32, 64],
        }
        grid_search = HyperparameterGridSearch(config=config, param_grid=param_grid, model_type=model_type)
        results = grid_search.run()
        logger.info("Grid search complete: %s", results["success"])

    return _handle_grid_search

