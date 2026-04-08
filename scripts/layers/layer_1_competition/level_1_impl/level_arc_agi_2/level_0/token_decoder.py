"""Token-level constrained decoder utilities for ARC LM mode."""

from dataclasses import dataclass
from math import log
from typing import Callable

Grid = list[list[int]]


@dataclass(frozen=True)
class TokenDecodeCandidate:
    grid: Grid
    score: float
    token_count: int


def _safe_log_prob(p: float) -> float:
    return float(log(max(1e-9, min(1.0, float(p)))))


def decode_tokens_to_grids(
    *,
    input_grid: Grid,
    token_probs_provider: Callable[[list[int]], dict[int, float]],
    beam_width: int,
    max_candidates: int,
    max_neg_log_score: float,
) -> list[TokenDecodeCandidate]:
    """Decode a fixed-shape grid via constrained token expansion.

    Token IDs are treated as ARC colors 0..9 for package-level decoding.
    """
    h = len(input_grid)
    w = len(input_grid[0]) if h else 0
    if h == 0 or w == 0:
        return [TokenDecodeCandidate(grid=[], score=0.0, token_count=0)]
    length = h * w
    beam: list[tuple[list[int], float]] = [([], 0.0)]
    for _step in range(length):
        next_beam: list[tuple[list[int], float]] = []
        for prefix, score in beam:
            probs = token_probs_provider(prefix)
            if not probs:
                continue
            items = sorted(probs.items(), key=lambda kv: kv[1], reverse=True)[: max(1, int(beam_width or 1))]
            for tok, prob in items:
                if int(tok) < 0 or int(tok) > 9:
                    continue
                ns = score + _safe_log_prob(float(prob))
                if -ns > float(max_neg_log_score):
                    continue
                next_beam.append((prefix + [int(tok)], ns))
        if not next_beam:
            break
        next_beam.sort(key=lambda kv: kv[1], reverse=True)
        beam = next_beam[: max(1, int(beam_width or 1))]

    out: list[TokenDecodeCandidate] = []
    for seq, score in beam[: max(1, int(max_candidates or 1))]:
        if len(seq) < length:
            seq = seq + [0] * (length - len(seq))
        grid = [seq[i * w : (i + 1) * w] for i in range(h)]
        out.append(TokenDecodeCandidate(grid=grid, score=float(score), token_count=len(seq)))
    return out
