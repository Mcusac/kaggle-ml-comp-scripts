"""Cross-validate command handler."""

import argparse

from typing import Any, Callable

from layers.layer_0_core.level_0 import get_arg, get_logger
from layers.layer_0_core.level_9 import CrossValidateWorkflow

from layers.layer_1_competition.level_0_infra.level_0 import create_pipeline_kwargs
from layers.layer_1_competition.level_0_infra.level_1.handlers.handler_context import setup_handler_context

logger = get_logger(__name__)


def make_handler(builder: Any) -> Callable[[argparse.Namespace], None]:
    def _handle_cross_validate(args: argparse.Namespace) -> None:
        contest_name, config, model_type, _, data_schema, paths = setup_handler_context(args=args, builder=builder)
        n_folds = get_arg(args, "n_folds", 5)
        train_data, _, _ = builder.load_contest_data(
            contest_name=contest_name,
            model_type=model_type,
            n_folds=n_folds,
        )
        pipeline_kwargs = create_pipeline_kwargs(paths, data_schema, model_type)
        workflow = CrossValidateWorkflow(config=config, n_folds=n_folds, train_data=train_data, **pipeline_kwargs)
        results = workflow.run()
        logger.info("Cross-validation complete: %s", results["success"])

    return _handle_cross_validate

