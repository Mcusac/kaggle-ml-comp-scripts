"""RNA3D training orchestrator pipeline.

Validates data, runs registered tier-2 trainers for each requested model name, and
writes artifacts under contest-scoped output directories.
"""

from pathlib import Path
from typing import List

from layers.layer_0_core.level_0 import get_logger, ensure_dir

from layers.layer_1_competition.level_1_impl.level_rna3d.level_0 import validate_rna3d_inputs, RNA3DPaths
from layers.layer_1_competition.level_1_impl.level_rna3d.level_2 import get_trainer, list_available_models
from layers.layer_1_competition.level_0_infra.level_0 import contest_models_dir
from layers.layer_1_competition.level_0_infra.level_1.contest import ValidateFirstRunner

_logger = get_logger(__name__)


def train_pipeline(
    data_root: str,
    train_mode: str,
    models: List[str],
    *,
    validate_first: bool = True,
) -> None:
    """Train one or more RNA3D models.

    Args:
        data_root: Directory containing competition CSVs.
        train_mode: Notebook/CLI label (e.g. ``end_to_end``); logged per model.
            Registered trainers are still called with ``(data_root, output_dir)`` only.
        models: Model names to train (e.g. ``[\"baseline_approx\"]``).
    """
    root = Path(data_root)
    if not root.exists():
        raise FileNotFoundError(f"data_root does not exist: {root}")

    def _run() -> None:
        paths = RNA3DPaths()
        output_base = contest_models_dir(paths, "rna3d")
        ensure_dir(output_base)

        available = list_available_models()
        for model_name in models:
            if model_name not in available:
                raise ValueError(
                    f"Model '{model_name}' not found. Available: {available}"
                )

            _logger.info("Training model: %s", model_name)
            _logger.info("  Train mode: %s", train_mode)

            trainer = get_trainer(model_name)
            if trainer is None:
                raise ValueError(f"No trainer registered for model '{model_name}'")

            model_output_dir = output_base / model_name
            ensure_dir(model_output_dir)

            try:
                trainer(data_root=data_root, output_dir=str(model_output_dir))
                _logger.info("  Completed: %s", model_output_dir)
            except Exception as e:
                _logger.error("  Failed to train %s: %s", model_name, e, exc_info=True)
                raise

        _logger.info("Training pipeline completed")

    if validate_first:
        return ValidateFirstRunner(
            validate_fn=validate_rna3d_inputs,
            run_fn=_run,
            data_root=data_root,
            max_targets=0,
        ).run()
    return _run()
