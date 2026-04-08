"""Compare ranking objectives on labeled candidate pools (offline)."""

from collections.abc import Callable, Sequence
from typing import TypeVar

T = TypeVar("T")


def tune_accuracy_at_k(
    rank_fn: Callable[[list[T]], list[T]],
    candidates: list[T],
    *,
    truth: T,
    k: int = 2,
    key: Callable[[T, T], bool] | None = None,
) -> bool:
    """Return True if any of the top-``k`` ranked items equals ``truth``."""
    eq = key or (lambda a, b: a == b)
    ranked = rank_fn(list(candidates))
    top = ranked[: max(1, int(k))]
    return any(eq(item, truth) for item in top)


def tune_compare_rankers(
    rankers: Sequence[tuple[str, Callable[[list[T]], list[T]]]],
    candidates: list[T],
    *,
    truth: T,
    k: int = 2,
    key: Callable[[T, T], bool] | None = None,
) -> dict[str, bool]:
    """Run each named ranker; return whether truth appears in top-k."""
    return {
        name: tune_accuracy_at_k(fn, candidates, truth=truth, k=k, key=key) for name, fn in rankers
    }
