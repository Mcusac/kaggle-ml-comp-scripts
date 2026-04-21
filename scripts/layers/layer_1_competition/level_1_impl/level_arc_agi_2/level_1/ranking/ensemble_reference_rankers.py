"""Reference notebook ensemble scoring (``score_kgmon``, ``score_full_probmul_3``).

Ports NVARC ``score_sum`` / ``getter_*`` behavior:

- **Merge**: same hash bucket as ``hashable(g["solution"])`` → ``tuple(map(tuple, guess))``
  after optional ``tolist()`` (not int-cast), matching notebook collisions/tie order.

- **Sort**: ``sorted(..., key=lambda x: x[0], reverse=True)`` on the aggregate score only.
  **Tie-break**: Python's sort is stable, so equal scores keep the relative order of merged
  groups as yielded by ``scores.values()`` — insertion order of first-seen hash keys,
  i.e. order of first occurrence of each distinct solution along ``list(guesses.values())``.

- **probmul** (``getter_full_probmul_3``): ``sum(baseline - beam) + mean_per_guess(sum(baseline - s for s in score_aug))``.
  An **empty** ``score_aug`` contributes inner sum **0** (not an extra ``baseline`` term).

- **kgmon** (``getter_kgmon``): ``len(guesses) - mean_guess(mean(score_aug))``.
  **Empty** ``score_aug`` → inner ``mean`` is **NaN** (like ``numpy.mean([])``), propagating
  to the outer mean like the reference.
"""

from typing import Any, Callable

from layers.layer_1_competition.level_0_infra.level_0 import grid_int_hash_key

Grid = list[list[int]]
GuessDict = dict[str, Any]


def reference_hashable_solution(solution: Any) -> tuple[tuple[Any, ...], ...]:
    """Notebook ``hashable`` (``tuple(map(tuple, guess))`` after ndarray ``tolist``)."""
    if hasattr(solution, "tolist"):
        solution = solution.tolist()
    return tuple(map(tuple, solution))


def ensemble_hashable_grid(solution: Any) -> tuple[tuple[int, ...], ...]:
    """Integer-normalized grid key (for non-notebook callers / ARC grids)."""
    return grid_int_hash_key(solution)


def _solution_as_grid(sol: Any) -> Grid:
    if hasattr(sol, "tolist"):
        sol = sol.tolist()
    return [[int(x) for x in row] for row in sol]


def _np_mean_empty_nan(values: list[float]) -> float:
    """Match ``numpy.mean`` on a Python list (empty → NaN)."""
    if not values:
        return float("nan")
    return float(sum(values) / len(values))


def ensemble_score_sum(
    guesses: dict[str, GuessDict],
    getter: Callable[[list[GuessDict]], float],
) -> list[Grid]:
    """Notebook ``score_sum``: merge by :func:`reference_hashable_solution`, sort by ``getter`` desc."""
    guess_list = list(guesses.values())
    scores: dict[tuple[tuple[Any, ...], ...], list[Any]] = {}
    for g in guess_list:
        h = reference_hashable_solution(g["solution"])
        if h not in scores:
            scores[h] = [[], g["solution"]]
        scores[h][0].append(g)
    scored: list[tuple[float, Any]] = [(getter(sc), o) for sc, o in scores.values()]
    scored.sort(key=lambda x: x[0], reverse=True)
    return [_solution_as_grid(x[-1]) for x in scored]


def _getter_full_probmul_3(guesses: list[GuessDict], baseline: float = 3.0) -> float:
    """Notebook ``getter_full_probmul_3`` (pure Python)."""
    inf_score = sum(float(baseline) - float(g["beam_score"]) for g in guesses)
    inner_sums: list[float] = [
        sum(float(baseline) - float(s) for s in g["score_aug"]) for g in guesses
    ]
    aug_score = _np_mean_empty_nan(inner_sums)
    return float(inf_score + aug_score)


def ensemble_score_full_probmul_3(guesses: dict[str, GuessDict]) -> list[Grid]:
    return ensemble_score_sum(guesses, _getter_full_probmul_3)


def _getter_kgmon(guesses: list[GuessDict]) -> float:
    """Notebook ``getter_kgmon`` (pure Python)."""
    inf_score = float(len(guesses))
    inner_means = [_np_mean_empty_nan([float(s) for s in g["score_aug"]]) for g in guesses]
    aug_score = _np_mean_empty_nan(inner_means)
    return float(inf_score - aug_score)


def ensemble_score_kgmon(guesses: dict[str, GuessDict]) -> list[Grid]:
    return ensemble_score_sum(guesses, _getter_kgmon)


ENSEMBLE_REFERENCE_RANKERS: dict[str, Callable[[dict[str, GuessDict]], list[Grid]]] = {
    "kgmon": ensemble_score_kgmon,
    "probmul": ensemble_score_full_probmul_3,
}