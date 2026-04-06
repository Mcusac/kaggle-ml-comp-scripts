"""Reference notebook-style ensemble scoring over decode guesses."""

from __future__ import annotations

import statistics
from typing import Any, Callable

Grid = list[list[int]]
GuessDict = dict[str, Any]


def ensemble_hashable_grid(solution: Any) -> tuple[tuple[int, ...], ...]:
    if hasattr(solution, "tolist"):
        solution = solution.tolist()
    return tuple(tuple(int(x) for x in row) for row in solution)


def ensemble_score_sum(
    guesses: dict[str, GuessDict],
    getter: Callable[[list[GuessDict]], float],
) -> list[Grid]:
    """Deduplicate by grid hash; sort merged groups by ``getter`` descending."""
    guess_list = list(guesses.values())
    merged: dict[tuple[tuple[int, ...], ...], list[GuessDict]] = {}
    for g in guess_list:
        h = ensemble_hashable_grid(g["solution"])
        merged.setdefault(h, []).append(g)
    scored: list[tuple[float, Grid]] = []
    for items in merged.values():
        key_score = float(getter(items))
        sol = items[0]["solution"]
        if hasattr(sol, "tolist"):
            sol = sol.tolist()
        scored.append((key_score, [list(row) for row in sol]))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [g for _, g in scored]


def _ensemble_getter_full_probmul_3(guesses: list[GuessDict], baseline: float = 3.0) -> float:
    if not guesses:
        return 0.0
    inf_score = sum(float(baseline) - float(g["beam_score"]) for g in guesses)

    def _aug_term(g: GuessDict) -> float:
        sa = g.get("score_aug") or [0.0]
        return sum(float(baseline) - float(s) for s in sa)

    aug_score = statistics.mean([_aug_term(g) for g in guesses])
    return float(inf_score + aug_score)


def ensemble_score_full_probmul_3(guesses: dict[str, GuessDict]) -> list[Grid]:
    return ensemble_score_sum(guesses, _ensemble_getter_full_probmul_3)


def _ensemble_getter_kgmon(guesses: list[GuessDict]) -> float:
    if not guesses:
        return 0.0
    inf_score = float(len(guesses))
    aug_score = statistics.mean(
        [float(statistics.mean(g.get("score_aug") or [0.0])) for g in guesses]
    )
    return inf_score - aug_score


def ensemble_score_kgmon(guesses: dict[str, GuessDict]) -> list[Grid]:
    return ensemble_score_sum(guesses, _ensemble_getter_kgmon)


ENSEMBLE_REFERENCE_RANKERS: dict[str, Callable[[dict[str, GuessDict]], list[Grid]]] = {
    "kgmon": ensemble_score_kgmon,
    "probmul": ensemble_score_full_probmul_3,
}
