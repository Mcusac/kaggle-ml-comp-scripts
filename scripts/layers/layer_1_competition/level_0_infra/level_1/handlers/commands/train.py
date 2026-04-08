"""Train command handler."""

import argparse

from typing import Any, Callable

from layers.layer_0_core.level_0 import get_arg, get_logger
from level_8 import TrainPipeline

from layers.layer_1_competition.level_0_infra.level_0 import create_pipeline_kwargs
from layers.layer_1_competition.level_0_infra.level_1.handlers.handler_context import setup_handler_context

logger = get_logger(__name__)


def make_handler(builder: Any) -> Callable[[argparse.Namespace], None]:
    def _handle_train(args: argparse.Namespace) -> None:
        contest_name, config, model_type, _, data_schema, paths = setup_handler_context(args=args, builder=builder)
        validation_split = get_arg(args, "validation_split", 0.2)
        train_data, val_data, _ = builder.load_contest_data(
            contest_name=contest_name,
            model_type=model_type,
            validation_split=validation_split,
        )
        pipeline_kwargs = create_pipeline_kwargs(paths, data_schema, model_type)
        train_pipeline = TrainPipeline(config=config, train_data=train_data, val_data=val_data, **pipeline_kwargs)
        results = train_pipeline.run()
        logger.info("Training complete: %s", results["success"])

    return _handle_train

