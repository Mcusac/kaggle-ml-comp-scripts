"""Variant result accumulation for grid search runs."""

from typing import Callable, Dict, List, Any, Set, Optional

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_1 import execute_variants

_logger = get_logger(__name__)


def accumulate_variant_results(
    variants: List[Any],
    run_variant_fn: Callable,
    create_key_fn: Callable,
    accumulated_results: Optional[List[Dict[str, Any]]] = None,
    accumulated_completed: Optional[Set] = None,
    save_results_fn: Callable = lambda: None,
    save_checkpoint_fn: Callable = lambda: None,
    score_key: str = 'score',
) -> Dict[str, Any]:
    """
    Run variants and merge results with any previously accumulated runs.

    Args:
        variants: List of variant configs to execute.
        run_variant_fn: Callable that executes a single variant.
        create_key_fn: Callable that produces a unique key for a variant.
        accumulated_results: Results carried over from prior runs (default: []).
        accumulated_completed: Completed variant keys from prior runs (default: set()).
        save_results_fn: Called after each variant to persist results.
        save_checkpoint_fn: Called after each variant to persist a checkpoint.
        score_key: Key used to extract the score from each result (default: 'score').

    Returns:
        Dict with keys: results, completed_variants, and any other fields
        returned by execute_variants.
    """
    accumulated_results = accumulated_results if accumulated_results is not None else []
    accumulated_completed = accumulated_completed if accumulated_completed is not None else set()

    core_summary = execute_variants(
        variants,
        run_variant_fn,
        create_key_fn,
        completed_variants=accumulated_completed,
        save_results_fn=save_results_fn,
        save_checkpoint_fn=save_checkpoint_fn,
        score_key=score_key,
    )

    accumulated_results.extend(core_summary['results'])

    return {
        **core_summary,
        'results': accumulated_results,
        'completed_variants': accumulated_completed,
    }