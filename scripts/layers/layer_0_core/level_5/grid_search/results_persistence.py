"""Bulk load and save of grid search result sets and checkpoint files."""

from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

from layers.layer_0_core.level_0 import extract_results_list, get_logger
from level_4 import load_json, save_json

logger = get_logger(__name__)


def load_results(
    results_file: Path,
) -> Tuple[List[Dict], float, Any, Set]:
    """
    Load a complete result set from a results file.

    Args:
        results_file: Path to the results JSON file.

    Returns:
        (results, best_score, best_variant, completed_variants)
    """
    try:
        data = load_json(results_file)
        results = extract_results_list(data)
        best_score = data.get('best_score', -float('inf'))
        best_variant = data.get('best_variant', None)
        completed_variants = {
            r.get('variant_key')
            for r in results
            if r.get('variant_key') is not None
        }
        logger.info(f"Loaded {len(results)} existing results")
        logger.info(f"Best score so far: {best_score:.4f}")
        return results, best_score, best_variant, completed_variants
    except Exception as e:
        logger.warning(f"Failed to load results: {e}")
        return [], -float('inf'), None, set()


def save_results(
    results_file: Path,
    grid_search_type: str,
    total_variants: int,
    completed_count: int,
    best_score: float,
    best_variant: Any,
    results: List[Dict[str, Any]],
) -> None:
    """
    Persist a complete result set to a results file.

    Args:
        results_file: Destination path.
        grid_search_type: Label identifying the search type.
        total_variants: Total number of variants in the search space.
        completed_count: Number of variants completed so far.
        best_score: Best CV score observed.
        best_variant: Variant configuration that produced best_score.
        results: Full list of per-variant result dicts.
    """
    save_json(
        {
            'grid_search_type': grid_search_type,
            'total_variants': total_variants,
            'completed_variants': completed_count,
            'best_score': best_score,
            'best_variant': best_variant,
            'results': results,
        },
        results_file,
    )


def load_checkpoint(
    checkpoint_dir: Optional[Path],
    param_grid: Optional[Dict] = None,
) -> Optional[Tuple[List[Dict], float, Any, Set]]:
    """
    Load the most recent checkpoint from a checkpoint directory.

    Selects the latest file matching checkpoint_*.json by timestamp suffix.
    Warns if the checkpoint's param_grid differs from the supplied one.

    Args:
        checkpoint_dir: Directory containing checkpoint files.
        param_grid: Current search param grid for consistency validation.

    Returns:
        (results, best_score, best_variant, completed_variants) or None if
        no checkpoint directory or files exist.
    """
    if checkpoint_dir is None or not checkpoint_dir.exists():
        return None

    checkpoint_files = list(checkpoint_dir.glob("checkpoint_*.json"))
    if not checkpoint_files:
        return None

    checkpoint_files.sort(key=_extract_checkpoint_timestamp, reverse=True)
    latest = checkpoint_files[0]

    try:
        logger.info(f"Loading checkpoint: {latest.name}")
        checkpoint = load_json(latest)

        if param_grid is not None:
            ckpt_grid = checkpoint.get('param_grid', {})
            if ckpt_grid != param_grid:
                logger.warning(
                    f"Checkpoint param_grid does not match current grid. "
                    f"Checkpoint: {ckpt_grid}, Current: {param_grid}"
                )

        results = checkpoint.get('all_results', [])
        best_score = checkpoint.get('best_score', -float('inf')) or -float('inf')
        best_variant = checkpoint.get('best_params', None)
        completed_variants = set(checkpoint.get('tested_variants', []))

        logger.info(f"Checkpoint loaded: {len(results)} results, best_score={best_score}")
        return results, best_score, best_variant, completed_variants

    except Exception as e:
        logger.warning(f"Failed to load checkpoint: {e}")
        return None


def save_checkpoint(
    checkpoint_dir: Optional[Path],
    grid_search_type: str,
    param_grid: Dict,
    results: List[Dict],
    best_variant: Any,
    best_score: float,
    completed_variants: Set,
    total_variants: int,
    quick_mode: bool,
) -> None:
    """
    Write a timestamped checkpoint file to checkpoint_dir.

    No-op when checkpoint_dir is None.

    Args:
        checkpoint_dir: Directory to write the checkpoint into.
        grid_search_type: Label identifying the search type.
        param_grid: Full parameter grid being searched.
        results: All results collected so far.
        best_variant: Best variant configuration seen so far.
        best_score: Best CV score seen so far.
        completed_variants: Set of variant keys already evaluated.
        total_variants: Total variants in the search space.
        quick_mode: Whether the search is running in quick mode.
    """
    if checkpoint_dir is None:
        return

    checkpoint = {
        'grid_search_type': grid_search_type,
        'param_grid': param_grid,
        'all_results': results,
        'best_params': best_variant,
        'best_score': float(best_score) if best_score != -float('inf') else None,
        'tested_variants': [str(v) for v in completed_variants],
        'total_variants': total_variants,
        'n_combinations_tested': len(completed_variants),
        'timestamp': datetime.now().isoformat(),
        'quick_mode': quick_mode,
    }

    checkpoint_file = checkpoint_dir / f"checkpoint_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        save_json(checkpoint, checkpoint_file)
        logger.debug(f"Checkpoint saved: {checkpoint_file.name}")
    except Exception as e:
        logger.warning(f"Failed to save checkpoint: {e}")


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _extract_checkpoint_timestamp(filepath: Path) -> str:
    """Extract the YYYYMMDD_HHMMSS suffix from a checkpoint filename for sorting."""
    parts = filepath.stem.split('_')
    if len(parts) >= 3:
        return '_'.join(parts[-2:])
    return '00000000_000000'