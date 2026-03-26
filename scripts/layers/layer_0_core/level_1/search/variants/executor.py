"""Grid search executor."""

from typing import Dict, List, Any, Callable, Set

from level_0 import get_logger

logger = get_logger(__name__)

def execute_variants(
    variants: List[Any],
    run_variant_fn: Callable[[Any, int], Dict[str, Any]],
    create_key_fn: Callable[[Any], Any],
    completed_variants: Set = None,
    save_results_fn: Callable[[], None] = lambda: None,
    save_checkpoint_fn: Callable[[], None] = lambda: None,
    score_key: str = 'score',
) -> Dict[str, Any]:
    """
    Core grid search execution: returns best score, best variant,
    results, and updated completed set.
    """
    completed_variants = completed_variants or set()
    results: List[Dict[str, Any]] = []
    best_score = -float('inf')
    best_variant: Dict[str, Any] = {}
    skipped: Set[Any] = set()

    total_variants = len(variants)

    for idx, variant in enumerate(variants):
        variant_key = create_key_fn(variant)
        if variant_key in completed_variants:
            continue

        try:
            variant_result = run_variant_fn(variant, idx)
            variant_result['variant_key'] = str(variant_key)
            variant_result['variant_index'] = idx
            results.append(variant_result)

            score = variant_result.get(score_key, -float('inf'))
            if score > best_score:
                best_score = score
                best_variant = variant_result

            completed_variants.add(variant_key)
            save_results_fn()
            save_checkpoint_fn()

        except Exception as e:
            logger.warning(
                "Variant %d failed: %s",
                idx,
                e,
                exc_info=True,
            ) 
            results.append({
                'variant_key': str(variant_key),
                'variant_index': idx,
                'success': False,
                'error': str(e),
                score_key: -float('inf'),
            })
            skipped.add(variant_key)
            save_results_fn()
            save_checkpoint_fn()

    return {
        'success': True,
        'total_variants': total_variants,
        'completed_variants': completed_variants,
        'failed_variants': skipped,
        'best_score': best_score,
        'best_variant': best_variant,
        'results': results,
    }