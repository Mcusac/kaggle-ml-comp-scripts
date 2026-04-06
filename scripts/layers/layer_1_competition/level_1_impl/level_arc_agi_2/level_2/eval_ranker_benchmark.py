"""Benchmark decoder rankers against labeled grids (reference notebook pattern)."""

from __future__ import annotations

from typing import Any, Callable

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.arc_grids_equal import (
    arc_grids_equal,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.ensemble_reference_rankers import (
    Grid,
    ensemble_score_full_probmul_3,
    ensemble_score_kgmon,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.arc_infer_artifact_store import (
    DecodedStore,
    GuessDict,
)


def eval_run_selection_on_decoded(
    decoded_results: DecodedStore,
    selection_fn: Callable[[dict[str, GuessDict]], list[Grid]],
) -> dict[str, list[Grid]]:
    """Per base key, apply ranker to that key's guess dict."""
    return {bk: selection_fn(dict(sub)) for bk, sub in decoded_results.items()}


def _eval_split_basekey(basekey: str) -> tuple[str, int]:
    if "_" not in basekey:
        return basekey, 0
    prefix, suf = basekey.rsplit("_", 1)
    if suf.isdigit():
        return prefix, int(suf)
    return basekey, 0


def _eval_num_tasks_per_puzzle(decoded_results: DecodedStore) -> dict[str, int]:
    out: dict[str, int] = {}
    for basekey in decoded_results:
        tid, idx = _eval_split_basekey(basekey)
        out[tid] = max(out.get(tid, 0), idx + 1)
    return out


def eval_benchmark_rankers(
    decoded_results: DecodedStore,
    labels: dict[str, Grid],
    *,
    n_guesses: int = 2,
    rankers: dict[str, Callable[[dict[str, GuessDict]], list[Grid]]] | None = None,
) -> dict[str, Any]:
    """Compare named rankers; return per-ranker accuracy and diagnostics."""
    if rankers is None:
        rankers = {
            "score_kgmon": ensemble_score_kgmon,
            "score_full_probmul_3": ensemble_score_full_probmul_3,
        }
    ntp = _eval_num_tasks_per_puzzle(decoded_results)
    num_puzzles = len(
        {_eval_split_basekey(k)[0] for k in labels}
    ) if labels else len(ntp) if ntp else 0
    results: dict[str, Any] = {}
    for name, fn in rankers.items():
        selected = eval_run_selection_on_decoded(decoded_results, fn)
        correct_puzzles: set[str] = set()
        for k, v in selected.items():
            if k not in labels:
                continue
            if any(arc_grids_equal(guess, labels[k]) for guess in v[: max(1, n_guesses)]):
                correct_puzzles.add(k)
        score = sum(1.0 / float(ntp.get(_eval_split_basekey(k)[0], 1)) for k in correct_puzzles)
        results[name] = {
            "correct_basekeys": sorted(correct_puzzles),
            "puzzle_weighted_score": float(score),
            "num_puzzles": int(num_puzzles),
        }
    return results


def eval_summarize_correct_beam_stats(
    decoded_results: DecodedStore,
    labels: dict[str, Grid],
) -> tuple[list[float], list[float]]:
    """Collect beam_score and mean(score_aug) for samples matching labels (for printing)."""
    correct_beam: list[float] = []
    correct_aug: list[float] = []
    for bk, samples in decoded_results.items():
        label = labels.get(bk)
        if label is None:
            continue
        for _sk, sample in samples.items():
            sol = sample.get("solution")
            if sol is None:
                continue
            if hasattr(sol, "tolist"):
                sol = sol.tolist()
            if not arc_grids_equal(sol, label):
                continue
            correct_beam.append(float(sample.get("beam_score", 0.0)))
            aug = sample.get("score_aug", [])
            if isinstance(aug, list) and aug:
                correct_aug.append(float(sum(float(x) for x in aug) / len(aug)))
            else:
                correct_aug.append(0.0)
    return correct_beam, correct_aug


def eval_safe_mean_max(values: list[float]) -> tuple[float | None, float | None]:
    """Guard empty sequences (reference notebook fix)."""
    if not values:
        return None, None
    return float(sum(values) / len(values)), float(max(values))
