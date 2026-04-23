"""Result loading and saving utilities for grid search."""

from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from layers.layer_0_core.level_0 import extract_results_list, get_logger
from layers.layer_0_core.level_4 import load_json, save_json

_logger = get_logger(__name__)


def load_completed_variants_helper(
    results_file: Optional[Path],
    keep_top_n: int,
    create_variant_key_from_result_fn: Callable[[Dict[str, Any]], Optional[Any]],
) -> Tuple[Set[Any], Set[Any], List[Dict[str, Any]], int]:
    """
    Load completed and skipped variants from results file.

    Args:
        results_file: Path to results file
        keep_top_n: Number of top variants to keep in memory
        create_variant_key_from_result_fn: Function to create variant key from result dict

    Returns:
        Tuple of (completed_variants_set, skipped_variants_set, top_variants_list, starting_index).
    """
    completed_variants = set()
    skipped_variants = set()
    top_variants = []

    if not results_file or not results_file.exists():
        return completed_variants, skipped_variants, top_variants, 0

    _logger.info(f"Loading completed variant keys from {results_file}")

    try:
        data = load_json(results_file)
        all_results = extract_results_list(data)
    except Exception as e:
        _logger.warning(f"Failed to load results file: {e}")
        return completed_variants, skipped_variants, top_variants, 0

    successful_count = 0
    skipped_count = 0
    failed_count = 0

    for r in all_results:
        variant_key = create_variant_key_from_result_fn(r)
        if variant_key is not None:
            if r.get('cv_score') is not None:
                completed_variants.add(variant_key)
                successful_count += 1
                top_variants.append(r)
            elif r.get('skipped', False):
                skipped_variants.add(variant_key)
                skipped_count += 1
            else:
                failed_count += 1

    top_variants.sort(key=lambda x: x.get('cv_score', -float('inf')), reverse=True)
    top_variants = top_variants[:keep_top_n]

    starting_index = get_next_variant_index(all_results)

    _logger.info(f"Found {successful_count} successfully completed variants")
    if skipped_count > 0:
        _logger.info(f"Found {skipped_count} skipped variants (persistent OOM - can retry later)")
    if failed_count > 0:
        _logger.info(f"Found {failed_count} failed variants (will be retried)")
    _logger.info(f"Tracking top {len(top_variants)} variant metadata in memory")
    _logger.info(f"Starting variant_index from {starting_index} (ensuring sequential numbering)")

    return completed_variants, skipped_variants, top_variants, starting_index


def get_next_variant_index(all_results: List[Dict[str, Any]]) -> int:
    """
    Get next variant index for sequential numbering.

    Args:
        all_results: List of all result dictionaries

    Returns:
        Next variant index to use.
    """
    if not all_results:
        return 0

    max_index = -1
    for r in all_results:
        idx = r.get('variant_index', -1)
        if isinstance(idx, int) and idx > max_index:
            max_index = idx

    return max_index + 1


def save_variant_result_helper(result: Dict[str, Any], results_file: Path) -> None:
    """
    Save variant result to results file (incremental append).

    Args:
        result: Variant result dictionary
        results_file: Path to results file
    """
    if results_file.exists():
        try:
            data = load_json(results_file)
            all_results = extract_results_list(data)
        except Exception:
            all_results = []
    else:
        all_results = []

    all_results.append(result)

    save_json(all_results, results_file)

    variant_id = result.get('variant_id', result.get('combination_id', 'unknown'))
    variant_index = result.get('variant_index', result.get('combination_index', 'unknown'))
    _logger.info(
        f"Results saved incrementally to {results_file} (variant {variant_id}, index {variant_index})"
    )
