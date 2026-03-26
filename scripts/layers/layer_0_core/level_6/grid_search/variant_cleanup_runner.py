"""Per-variant and periodic checkpoint cleanup orchestration during grid search."""

import shutil

from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

from layers.layer_0_core.level_0 import extract_results_list, get_logger
from level_4 import load_json
from level_5 import cleanup_grid_search_checkpoints_retroactive

logger = get_logger(__name__)


def _get_cleanup_config(
    config: Union[Any, Dict[str, Any]],
) -> Tuple[bool, int, int, bool]:
    """Extract cleanup settings from config object or dict. Returns (enable_cleanup, keep_top_n, cleanup_interval, delete_checkpoints)."""
    if isinstance(config, dict):
        return (
            config.get("enable_cleanup", False),
            config.get("keep_top_variants", 5),
            config.get("cleanup_interval", 10),
            config.get("delete_checkpoints_after_completion", True),
        )
    gs = getattr(config, "grid_search", None)
    if gs is None:
        return False, 5, 10, True
    return (
        getattr(gs, "enable_cleanup", False),
        getattr(gs, "keep_top_variants", 5),
        getattr(gs, "cleanup_interval", 10),
        getattr(gs, "delete_checkpoints_after_completion", True),
    )


def run_variant_cleanup(
    config: Union[Any, Dict[str, Any]],
    base_model_dir: Path,
    results_file: Path,
    variant_model_dir: Path,
    cv_score: Optional[float],
    variant_id: str,
) -> None:
    """
    Run all configured cleanup steps after a single variant completes.

    Executes three cleanup passes in order:
    1. Immediate deletion of this variant's checkpoints (if configured).
    2. Prune to top-N across all variants so far (if configured).
    3. Periodic bulk prune every N variants (if configured).

    Args:
        config: Configuration object or dict with grid_search cleanup settings.
        base_model_dir: Root directory containing all variant subdirectories.
        results_file: Path to the running results JSON file.
        variant_model_dir: Checkpoint directory for the just-completed variant.
        cv_score: CV score for this variant, or None if the variant failed.
        variant_id: String identifier of the variant.
    """
    delete_variant_checkpoints_immediately(config, variant_model_dir, cv_score, variant_id)
    cleanup_top_variants(config, base_model_dir, results_file, cv_score)
    completed_count = get_completed_count(results_file)
    run_periodic_cleanup(config, base_model_dir, results_file, completed_count)


def delete_variant_checkpoints_immediately(
    config: Union[Any, Dict[str, Any]],
    variant_model_dir: Path,
    cv_score: Optional[float],
    variant_id: str,
) -> None:
    """
    Delete a variant's checkpoint directory immediately after it completes.

    Only deletes when the variant succeeded (cv_score is not None) and
    delete_checkpoints_after_completion is True in config.

    Args:
        config: Configuration object or dict.
        variant_model_dir: Checkpoint directory to delete.
        cv_score: CV score for this variant, or None if it failed.
        variant_id: String identifier used in log messages.
    """
    _, _, _, delete_checkpoints = _get_cleanup_config(config)
    if cv_score is not None and delete_checkpoints:
        logger.info(f"Deleting checkpoints for variant {variant_id} (results saved to results.json)")
        try:
            if variant_model_dir.exists():
                shutil.rmtree(variant_model_dir)
                logger.info(f"Deleted variant checkpoints: {variant_model_dir}")
        except Exception as e:
            logger.warning(f"Failed to delete variant checkpoints: {e}")


def cleanup_top_variants(
    config: Union[Any, Dict[str, Any]],
    base_model_dir: Path,
    results_file: Path,
    cv_score: Optional[float],
) -> None:
    """
    Prune all variants outside the top N immediately after a successful variant.

    No-op when enable_cleanup is False or when cv_score is None (variant failed).

    Args:
        config: Configuration object or dict.
        base_model_dir: Root directory containing all variant subdirectories.
        results_file: Path to the running results JSON file.
        cv_score: CV score for the just-completed variant, or None if failed.
    """
    enable_cleanup, keep_top_n, _, _ = _get_cleanup_config(config)
    if not enable_cleanup or cv_score is None:
        return

    try:
        deleted, freed = cleanup_grid_search_checkpoints_retroactive(
            model_base_dir=base_model_dir,
            results_file=results_file,
            keep_top_n=keep_top_n,
        )
        if deleted > 0:
            logger.info(f"Pruned {deleted} variants, freed {freed / (1024 * 1024):.2f} MB")
    except Exception as e:
        logger.warning(f"Failed to prune top variants: {e}")


def run_periodic_cleanup(
    config: Union[Any, Dict[str, Any]],
    base_model_dir: Path,
    results_file: Path,
    completed_count: int,
) -> None:
    """
    Run a bulk prune every cleanup_interval completed variants.

    No-op when enable_cleanup is False or the interval has not been reached.

    Args:
        config: Configuration object or dict.
        base_model_dir: Root directory containing all variant subdirectories.
        results_file: Path to the running results JSON file.
        completed_count: Total number of successfully completed variants so far.
    """
    enable_cleanup, keep_top_n, cleanup_interval, _ = _get_cleanup_config(config)
    if not enable_cleanup:
        return

    if completed_count > 0 and completed_count % cleanup_interval == 0:
        logger.info(f"Running periodic checkpoint cleanup (every {cleanup_interval} variants)")
        try:
            deleted, freed = cleanup_grid_search_checkpoints_retroactive(
                model_base_dir=base_model_dir,
                results_file=results_file,
                keep_top_n=keep_top_n,
            )
            if deleted > 0:
                logger.info(
                    f"Periodic cleanup: deleted {deleted} variants, "
                    f"freed {freed / (1024 * 1024):.2f} MB"
                )
        except Exception as e:
            logger.warning(f"Periodic cleanup failed: {e}")


def get_completed_count(results_file: Path) -> int:
    """
    Count successfully scored variants in the results file.

    Args:
        results_file: Path to the running results JSON file.

    Returns:
        Number of result entries with a non-None cv_score, or 0 if the
        file does not exist or cannot be read.
    """
    if not results_file or not results_file.exists():
        return 0
    try:
        data = load_json(results_file)
        all_results = extract_results_list(data)
        return len([r for r in all_results if r.get("cv_score") is not None])
    except Exception:
        return 0


def run_final_cleanup(
    config: Union[Any, Dict[str, Any]],
    base_model_dir: Path,
    results_file: Optional[Path],
) -> None:
    """
    Run a final prune pass at the end of the entire grid search.

    No-op when enable_cleanup is False or results_file is None.

    Args:
        config: Configuration object or dict.
        base_model_dir: Root directory containing all variant subdirectories.
        results_file: Path to the completed results JSON file, or None.
    """
    enable_cleanup, keep_top_n, _, _ = _get_cleanup_config(config)
    if not enable_cleanup or not results_file:
        return

    logger.info("Running final checkpoint cleanup")
    try:
        deleted, freed = cleanup_grid_search_checkpoints_retroactive(
            model_base_dir=base_model_dir,
            results_file=results_file,
            keep_top_n=keep_top_n,
        )
        if deleted > 0:
            logger.info(
                f"Final cleanup: deleted {deleted} variants, "
                f"freed {freed / (1024 * 1024):.2f} MB"
            )
        else:
            completed = get_completed_count(results_file)
            logger.info(f"Final cleanup: nothing to delete ({completed} variants retained)")
    except Exception as e:
        logger.warning(f"Final cleanup failed: {e}")
