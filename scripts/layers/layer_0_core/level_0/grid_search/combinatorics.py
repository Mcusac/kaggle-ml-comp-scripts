"""Combinatorics utilities for grid search parameter exploration."""

from typing import List, Tuple, TypeVar
from itertools import combinations

T = TypeVar("T")


def generate_power_set(items: List[T]) -> List[Tuple[T, ...]]:
    """
    Generate all possible subsets (power set) of items.

    The power set includes the empty set and all combinations from size 0 to n.
    Results are sorted for consistency. Items must be sortable (e.g. str, int);
    non-sortable types will raise TypeError.

    Args:
        items: List of items to generate power set from (must be sortable)

    Returns:
        List of tuples, each representing a subset (sorted for consistency)

    Example:
        >>> generate_power_set(['a', 'b', 'c'])
        [(), ('a',), ('b',), ('c',), ('a', 'b'), ('a', 'c'), ('b', 'c'), ('a', 'b', 'c')]
    """
    power_set = []
    n = len(items)

    # Generate all combinations of all sizes (0 to n)
    for r in range(n + 1):
        for combo in combinations(items, r):
            power_set.append(tuple(sorted(combo)))

    return power_set
