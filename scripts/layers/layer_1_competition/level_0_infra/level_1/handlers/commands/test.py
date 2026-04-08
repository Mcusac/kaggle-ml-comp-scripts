"""Test (predict) command handler."""

import argparse

from typing import Any, Callable

from layers.layer_0_core.level_0 import get_arg, get_logger
from layers.layer_0_core.level_6 import PredictPipeline

from layers.layer_1_competition.level_0_infra.level_0 import create_pipeline_kwargs
from layers.layer_1_competition.level_0_infra.level_1.handlers.handler_context import setup_handler_context

logger = get_logger(__name__)


def make_handler(builder: Any) -> Callable[[argparse.Namespace], None]:
    def _handle_test(args: argparse.Namespace) -> None:
        contest_name, config, model_type, _, _, paths = setup_handler_context(args=args, builder=builder)
        model_path = get_arg(args, "model_path")
        if not model_path:
            raise ValueError("--model-path is required for test command")
        use_tta = getattr(args, "use_tta", False)
        _, _, test_data = builder.load_contest_data(contest_name=contest_name, model_type=model_type)
        pipeline_kwargs = create_pipeline_kwargs(paths, None, model_type)
        predict_pipeline = PredictPipeline(
            config=config,
            model_path=model_path,
            use_tta=use_tta,
            test_data=test_data,
            **pipeline_kwargs,
        )
        results = predict_pipeline.run()
        logger.info("Prediction complete: %s", results["success"])

    return _handle_test

