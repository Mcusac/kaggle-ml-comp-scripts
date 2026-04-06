"""Constrained DFS/beam decoder for ARC color-token grids."""

from __future__ import annotations

from dataclasses import dataclass
from math import log


@dataclass(frozen=True)
class GridCandidate:
    """A decoded candidate grid with cumulative score."""

    grid: list[list[int]]
    score: float


def _top_k_with_log_probs(probs: list[float], top_k: int) -> list[tuple[int, float]]:
    pairs = [(idx, float(p)) for idx, p in enumerate(probs)]
    pairs.sort(key=lambda kv: kv[1], reverse=True)
    selected = pairs[: max(1, int(top_k or 1))]
    out: list[tuple[int, float]] = []
    for color, prob in selected:
        safe = max(1e-9, min(1.0, float(prob)))
        out.append((int(color), float(log(safe))))
    return out


def decode_grid_candidates(
    cell_color_probs: list[list[list[float]]],
    *,
    beam_width: int = 16,
    max_candidates: int = 8,
    max_neg_log_score: float = 200.0,
) -> list[GridCandidate]:
    """Decode color grids from per-cell distributions.

    Args:
        cell_color_probs: shape [H][W][10], where each distribution is a color probability vector.
    """
    if not cell_color_probs:
        return [GridCandidate(grid=[], score=0.0)]
    h = len(cell_color_probs)
    w = len(cell_color_probs[0]) if h else 0
    if any(len(row) != w for row in cell_color_probs):
        raise ValueError("cell_color_probs rows must share width.")
    if any(len(cell) != 10 for row in cell_color_probs for cell in row):
        raise ValueError("Each cell distribution must contain 10 color probabilities.")

    expanded: list[list[tuple[int, float]]] = []
    for r in range(h):
        for c in range(w):
            expanded.append(_top_k_with_log_probs(cell_color_probs[r][c], top_k=max(2, beam_width // 4)))

    beam: list[tuple[list[int], float]] = [([], 0.0)]
    for options in expanded:
        next_beam: list[tuple[list[int], float]] = []
        for prefix, score in beam:
            for color, logp in options:
                new_score = score + logp
                if -new_score > float(max_neg_log_score):
                    continue
                next_beam.append((prefix + [int(color)], new_score))
        if not next_beam:
            break
        next_beam.sort(key=lambda kv: kv[1], reverse=True)
        beam = next_beam[: max(1, int(beam_width or 1))]

    candidates: list[GridCandidate] = []
    for flat, score in beam[: max(1, int(max_candidates or 1))]:
        rows = [flat[i * w : (i + 1) * w] for i in range(h)]
        candidates.append(GridCandidate(grid=rows, score=float(score)))
    return candidates
