"""Grid search checkpoint pruning: delete non-top-N variant directories."""

import shutil

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from layers.layer_0_core.level_0 import extract_results_list, get_logger
from level_4 import load_json

logger = get_logger(__name__)


def _delete_non_top_dirs(
    candidate_dirs: List[Path],
    keep_names: Set[str],
) -> Tuple[int, int]:
    """
    Delete directories whose names are not in keep_names.

    Args:
        candidate_dirs: All variant directories to consider.
        keep_names: Directory names that must not be deleted.

    Returns:
        (variants_deleted, bytes_freed)
    """
    deleted = 0
    freed = 0
    for d in candidate_dirs:
        if d.name in keep_names:
            continue
        try:
            size = sum(f.stat().st_size for f in d.rglob('*') if f.is_file())
            shutil.rmtree(d)
            deleted += 1
            freed += size
            logger.debug(f"Deleted variant directory: {d}")
        except Exception as e:
            logger.warning(f"Failed to delete {d}: {e}")
    return deleted, freed


def cleanup_grid_search_checkpoints_retroactive(
    model_base_dir: str,
    results_file: str,
    keep_top_n: int = 20,
) -> Tuple[int, int]:
    """
    Delete checkpoints for all variants outside the top N by CV score.

    Searches both 'dataset_grid_search' and 'hyperparameter_grid_search'
    subdirectories under model_base_dir. Variants are identified by their
    directory name matching the variant_id field in the results file.

    Args:
        model_base_dir: Base directory containing grid search subdirectories.
        results_file: Path to JSON results file produced by the grid search.
        keep_top_n: Number of top-scoring variants to retain (default: 20).

    Returns:
        (variants_deleted, bytes_freed): Count of deleted directories and
        approximate bytes reclaimed.
    """
    model_base_dir = Path(model_base_dir)
    results_file = Path(results_file)

    if not results_file.exists():
        logger.warning(f"Results file not found: {results_file}")
        return 0, 0

    try:
        data = load_json(results_file)
        all_results = extract_results_list(data)
    except Exception as e:
        logger.error(f"Failed to load results file: {e}")
        return 0, 0

    successful = [r for r in all_results if r.get('cv_score') is not None]
    if not successful:
        logger.info("No successful results found")
        return 0, 0

    successful.sort(key=lambda x: x.get('cv_score', -float('inf')), reverse=True)
    keep_ids: Set[str] = {
        r['variant_id']
        for r in successful[:keep_top_n]
        if r.get('variant_id')
    }
    logger.info(f"Keeping top {len(keep_ids)} variants")

    total_deleted = 0
    total_freed = 0
    for subdir_name in ('dataset_grid_search', 'hyperparameter_grid_search'):
        subdir = model_base_dir / subdir_name
        if not subdir.exists():
            continue
        candidate_dirs = [d for d in subdir.iterdir() if d.is_dir()]
        deleted, freed = _delete_non_top_dirs(candidate_dirs, keep_ids)
        total_deleted += deleted
        total_freed += freed

    if total_deleted > 0:
        logger.info(
            f"Cleanup complete: deleted {total_deleted} variants, "
            f"freed {total_freed / (1024 * 1024):.2f} MB"
        )
    else:
        logger.info("No variants to delete (all within top N)")

    return total_deleted, total_freed


def cleanup_checkpoints(
    grid_search_dir: Path,
    keep_top_n: int = 5,
    results: Optional[List[Dict[str, Any]]] = None,
) -> None:
    """
    Delete variant checkpoints outside the top N by score from a results list.

    Variant directories must follow the naming pattern 'variant_<index>'.
    Variants are ranked by the 'score' key in results.

    Args:
        grid_search_dir: Directory containing variant subdirectories.
        keep_top_n: Number of top-scoring variants to retain (default: 5).
        results: Pre-loaded list of result dicts, each with 'success',
                 'score', and 'variant_index' keys. If None, skips cleanup.
    """
    logger.info(f"Cleaning up checkpoints (keeping top {keep_top_n})...")

    if results is None:
        logger.warning("No results provided — cannot determine top variants. Skipping.")
        return

    sorted_results = sorted(
        [r for r in results if r.get('success', False)],
        key=lambda x: x.get('score', -float('inf')),
        reverse=True,
    )
    top_indices = {r.get('variant_index') for r in sorted_results[:keep_top_n]}
    keep_names: Set[str] = {f'variant_{i}' for i in top_indices if i is not None}

    candidate_dirs = [
        d for d in grid_search_dir.iterdir()
        if d.is_dir() and d.name.startswith('variant_')
    ]
    deleted, _ = _delete_non_top_dirs(candidate_dirs, keep_names)
    logger.info(
        f"Cleanup complete: removed {deleted} variant directories, "
        f"kept {len(keep_names)} top variants."
    )
