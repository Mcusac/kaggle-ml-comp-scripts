"""Train + test workflow command handler."""

import argparse

from typing import Any, Callable

from layers.layer_0_core.level_0 import get_arg, get_logger
from layers.layer_0_core.level_9 import TrainPredictWorkflow

from layers.layer_1_competition.level_0_infra.level_0 import create_pipeline_kwargs, setup_handler_context

_logger = get_logger(__name__)


def make_handler(builder: Any) -> Callable[[argparse.Namespace], None]:
    def _handle_train_test(args: argparse.Namespace) -> None:
        contest_name, config, model_type, _, data_schema, paths = setup_handler_context(args=args, builder=builder)
        use_tta = getattr(args, "use_tta", False)
        validation_split = get_arg(args, "validation_split", 0.2)
        train_data, val_data, test_data = builder.load_contest_data(
            contest_name=contest_name,
            model_type=model_type,
            validation_split=validation_split,
        )
        pipeline_kwargs = create_pipeline_kwargs(paths, data_schema, model_type)
        workflow = TrainPredictWorkflow(
            config=config,
            use_tta=use_tta,
            train_data=train_data,
            val_data=val_data,
            test_data=test_data,
            **pipeline_kwargs,
        )
        results = workflow.run()
        _logger.info("Train-test workflow complete: %s", results["success"])

    return _handle_train_test

