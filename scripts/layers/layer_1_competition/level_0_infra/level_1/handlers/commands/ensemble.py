"""Ensemble command handler."""

import argparse

from pathlib import Path
from typing import Any, Callable

import numpy as np

from layers.layer_0_core.level_0 import ensure_dir, get_arg, get_logger, parse_comma_separated
from layers.layer_0_core.level_2 import simple_average

logger = get_logger(__name__)


def make_handler(builder: Any) -> Callable[[argparse.Namespace], None]:
    def _handle_ensemble(args: argparse.Namespace) -> None:
        model_paths_str = get_arg(args, "model_paths")
        if not model_paths_str:
            raise ValueError("--model-paths is required for ensemble command")
        model_paths = parse_comma_separated(model_paths_str)
        if not model_paths:
            raise ValueError("--model-paths cannot be empty")
        predictions_list = []
        for model_path in model_paths:
            pred_path = Path(model_path) / "predictions" / "predictions.npy"
            if pred_path.exists():
                predictions_list.append(np.load(pred_path))
            else:
                logger.warning("Predictions not found for %s, skipping", model_path)
        if not predictions_list:
            raise ValueError("No valid predictions found")
        weights = None
        weights_str = get_arg(args, "weights")
        if weights_str:
            weights = [float(w) for w in weights_str.split(",")]
            if len(weights) != len(predictions_list):
                raise ValueError(
                    f"Number of weights ({len(weights)}) must match number of models ({len(predictions_list)})"
                )
        ensemble_pred = simple_average(predictions_list, weights=weights)
        output_path = Path("output") / "ensemble_predictions.npy"
        ensure_dir(output_path.parent)
        np.save(output_path, ensemble_pred)
        logger.info("Ensemble complete. Saved to %s", output_path)

    return _handle_ensemble

