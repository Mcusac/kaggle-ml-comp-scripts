"""Export-model command handler."""

import argparse

from typing import Any, Callable

from layers.layer_0_core.level_0 import get_arg, get_logger
from layers.layer_0_core.level_5 import ExportPipeline

from layers.layer_1_competition.level_0_infra.level_0 import setup_handler_context

logger = get_logger(__name__)


def make_handler(builder: Any) -> Callable[[argparse.Namespace], None]:
    def _handle_export(args: argparse.Namespace) -> None:
        _, config, _, _, _, _ = setup_handler_context(args=args, builder=builder)
        model_path = get_arg(args, "model_path")
        if not model_path:
            raise ValueError("--model-path is required for export command")
        export_dir = get_arg(args, "export_dir", "output/exports")
        export_pipeline = ExportPipeline(config=config, model_path=model_path, export_dir=export_dir)
        results = export_pipeline.run()
        logger.info("Export complete: %s", results["success"])

    return _handle_export

