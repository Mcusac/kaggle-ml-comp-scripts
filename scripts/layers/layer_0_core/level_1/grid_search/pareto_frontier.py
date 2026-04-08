"""Pareto-optimal result selection for multi-objective optimization."""

from typing import List, Dict, Any

from level_0 import filter_successful_results, worst_case_metric_sentinel


def _dominates(
    other: Dict[str, Any],
    candidate: Dict[str, Any],
    metric_keys: List[str],
    maximize: List[bool],
) -> bool:
    """True if other dominates candidate (better or equal in all, strictly better in at least one)."""
    strictly_better_in_any = False
    for metric, should_max in zip(metric_keys, maximize):
        candidate_val = candidate.get(metric, worst_case_metric_sentinel(should_max))
        other_val = other.get(metric, worst_case_metric_sentinel(should_max))
        if should_max:
            if other_val > candidate_val:
                strictly_better_in_any = True
            elif other_val < candidate_val:
                return False
        else:
            if other_val < candidate_val:
                strictly_better_in_any = True
            elif other_val > candidate_val:
                return False
    return strictly_better_in_any


def get_pareto_frontier(
    results: List[Dict[str, Any]],
    metric_keys: List[str],
    maximize: List[bool]
) -> List[Dict[str, Any]]:
    """
    Get Pareto-optimal results for multi-objective optimization.

    Returns results that are not dominated by any other result across
    all specified metrics.

    Args:
        results: List of result dictionaries
        metric_keys: List of metric keys to consider
        maximize: List of bools indicating if each metric should be maximized

    Returns:
        List of Pareto-optimal results

    Example:
        >>> # Trade-off between accuracy (max) and latency (min)
        >>> pareto = get_pareto_frontier(
        ...     results,
        ...     metric_keys=['accuracy', 'latency_ms'],
        ...     maximize=[True, False]
        ... )
    """
    if not results:
        raise ValueError("Results list cannot be empty")
    if len(metric_keys) != len(maximize):
        raise ValueError("metric_keys and maximize must have same length")

    successful = filter_successful_results(results)
    if not successful:
        return []

    pareto_optimal = []
    for candidate in successful:
        is_dominated = False
        for other in successful:
            if candidate is other:
                continue
            if _dominates(other, candidate, metric_keys, maximize):
                is_dominated = True
                break
        if not is_dominated:
            pareto_optimal.append(candidate)

    return pareto_optimal
