"""Result aggregation and filtering for experiment management.

Provides utilities for ranking, filtering, and selecting results from
hyperparameter tuning, cross-validation, and model comparison experiments.
"""

from typing import List, Dict, Any, Callable


def filter_successful_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter to results with success=True."""
    return [r for r in results if r.get('success', False)]


def worst_case_metric_sentinel(maximize: bool) -> float:
    """Value used when metric is missing (worst possible for ranking)."""
    return float('-inf') if maximize else float('inf')


def get_best_variant(
    results: List[Dict[str, Any]],
    metric_key: str = 'score',
    maximize: bool = True
) -> Dict[str, Any]:
    """
    Get the single best variant from experiment results.

    Filters to successful results and returns the one with the best metric value.

    Args:
        results: List of result dictionaries, each containing:
                - 'success': bool indicating if experiment succeeded
                - metric_key: numeric value for ranking
                - other fields: experiment metadata (parameters, logs, etc.)
        metric_key: Key to use for ranking (default: 'score')
        maximize: If True, higher is better; if False, lower is better

    Returns:
        Best result dictionary with optimal metric value

    Raises:
        ValueError: If results list is empty or no successful results found

    Example:
        >>> results = [
        ...     {'success': True, 'score': 0.85, 'params': {'lr': 0.01}},
        ...     {'success': True, 'score': 0.92, 'params': {'lr': 0.1}},
        ...     {'success': False, 'score': None, 'params': {'lr': 0.5}},
        ... ]
        >>> best = get_best_variant(results)
        >>> best['score']
        0.92
    """
    top_results = get_top_n_variants(results, n=1, metric_key=metric_key, maximize=maximize)

    if not top_results:
        raise ValueError("No successful results found in results list")

    return top_results[0]


def get_top_n_variants(
    results: List[Dict[str, Any]],
    n: int = 5,
    metric_key: str = 'score',
    maximize: bool = True
) -> List[Dict[str, Any]]:
    """
    Get top N variants from experiment results.

    Filters to successful results and returns the top N ranked by metric value.

    Args:
        results: List of result dictionaries
        n: Number of top results to return (default: 5)
        metric_key: Key to use for ranking (default: 'score')
        maximize: If True, higher is better; if False, lower is better

    Returns:
        List of top N result dictionaries sorted by metric.
        Returns fewer than N if fewer successful results exist.

    Raises:
        ValueError: If results list is empty or n <= 0

    Example:
        >>> top_5 = get_top_n_variants(results, n=5)
        >>> for rank, variant in enumerate(top_5, 1):
        ...     print(f"Rank {rank}: score={variant['score']}")
    """
    if not results:
        raise ValueError("Results list cannot be empty")
    if n <= 0:
        raise ValueError("n must be positive")

    successful = filter_successful_results(results)
    if not successful:
        return []

    sentinel = worst_case_metric_sentinel(maximize)
    sorted_results = sorted(
        successful,
        key=lambda x: x.get(metric_key, sentinel),
        reverse=maximize
    )

    return sorted_results[:n]


def filter_results(
    results: List[Dict[str, Any]],
    predicate: Callable[[Dict[str, Any]], bool]
) -> List[Dict[str, Any]]:
    """
    Filter results by a custom predicate function.

    Args:
        results: List of result dictionaries
        predicate: Function that takes a result dict and returns bool

    Returns:
        Filtered list of results

    Example:
        >>> # Filter to results with score > 0.9
        >>> high_scorers = filter_results(
        ...     results,
        ...     lambda r: r.get('success') and r.get('score', 0) > 0.9
        ... )
    """
    return [r for r in results if predicate(r)]
