"""Train/export mode detection utilities."""

from typing import Optional
from pathlib import Path

from level_0 import get_logger
from level_1 import print_config_section
from level_7 import auto_detect_grid_search_results

logger = get_logger(__name__)


def detect_train_export_mode(
    model_name: Optional[str],
    fresh_train: bool
) -> str:
    """
    Detect train/export mode and auto-detect grid search results.

    Auto-detects grid search results file, validates fresh_train parameter, and displays
    appropriate mode message.

    Args:
        model_name: Optional model name for model-specific folder structure
        fresh_train: Whether to start fresh (delete directory) or resume from checkpoints

    Returns:
        Path to grid search results file as string

    Raises:
        FileNotFoundError: If no grid search results found
        RuntimeError: If results file detection fails or if parameters are invalid
        TypeError: If fresh_train is not a boolean value
    """
    # Validate boolean parameter
    if not isinstance(fresh_train, bool):
        raise TypeError(f"fresh_train must be a boolean, got {type(fresh_train).__name__}")

    try:
        results_file = auto_detect_grid_search_results(model_name=model_name)
    except FileNotFoundError as e:
        logger.error("\n❌ ERROR: No grid search results found")
        logger.error("=" * 60)
        logger.error("Cell 2a requires completed grid search results.")
        logger.error("Please run Cell 1a and/or Cell 1b first to find optimal hyperparameters.")
        logger.error("=" * 60)
        raise RuntimeError(str(e)) from e

    # Ensure results_file is a string
    results_file = str(results_file)

    # Display mode based on fresh_train
    if fresh_train:
        mode_name = "Train Fresh Model"
        action = "Delete directory if all folds complete, start fresh (--fresh-train)"
        note = "Uses hyperparameters from best variant in results"
    else:
        mode_name = "Train with Resume"
        action = "Preserve directory, resume from checkpoints (--no-fresh-train)"
        note = "Will resume incomplete folds automatically"

    print_config_section(
        f"📦 MODE: {mode_name}",
        {
            "Grid search results": Path(results_file).name,
            "Action": action,
            "Note": note
        }
    )

    return results_file
