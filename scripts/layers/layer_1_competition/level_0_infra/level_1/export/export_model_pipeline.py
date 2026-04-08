"""Export model pipeline. Requires contest_context from contest layer."""

from pathlib import Path
from typing import Optional, Any

from layers.layer_0_core.level_0 import ensure_dir, get_logger

from layers.layer_1_competition.level_0_infra.level_1.export.source_handlers import (
    handle_best_variant_file,
    handle_just_trained_model,
    handle_results_file,
)

logger = get_logger(__name__)


def export_model_pipeline(
    contest_context: Any,
    data_root: Optional[str] = None,
    results_file: Optional[str] = None,
    variant_id: Optional[str] = None,
    best_variant_file: Optional[str] = None,
    export_dir: Optional[str] = None,
    model_dir: Optional[str] = None,
    **kwargs
) -> str:
    """
    Export trained model for submission. Contest passes contest_context.
    """
    paths = contest_context.get_paths()
    config = contest_context.get_config()

    # Resolve export directory
    if export_dir is None:
        export_dir = str(paths.get_models_base_dir() / 'exports')
    ensure_dir(Path(export_dir))

    # Determine export scenario and handle
    if model_dir:
        # Scenario 1: Just-trained model
        logger.info(f"Exporting just-trained model from: {model_dir}")
        export_path, metadata = handle_just_trained_model(
            model_dir=model_dir,
            config=config,
            variant_id=variant_id,
            variant_info=kwargs.get('variant_info')
        )
    elif best_variant_file:
        # Scenario 2: Best variant from file
        export_path, metadata = handle_best_variant_file(
            best_variant_file=best_variant_file,
            config=config,
            export_dir=export_dir,
            paths=paths,
        )
    elif results_file and variant_id:
        # Scenario 3: Variant from results file
        export_path, metadata = handle_results_file(
            results_file=results_file,
            variant_id=variant_id,
            config=config,
            export_dir=export_dir,
            paths=paths,
        )
    else:
        # Scenario 4: Scan models base dir (auto-detect). For now, export from base dir.
        scan_dir = model_dir or str(paths.get_models_base_dir())
        logger.info(f"Exporting model from: {scan_dir}")
        export_path, metadata = handle_just_trained_model(model_dir=scan_dir, config=config)

    logger.info(f"✅ Model exported to: {export_path}")

    return str(export_path)
