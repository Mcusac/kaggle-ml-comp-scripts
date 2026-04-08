"""Augmentation-aware teacher-forced scoring (reference ``calc_scores`` + helpers).

Ports NVARC notebook batching: pad with ``PAD_ID``, one forward with ``use_cache=True``,
``logits.float().cpu().log_softmax(-1)``, then slice ``[query_len-1:query_len-1+answer_len]``
and sum log-probs on gold answer tokens (return **NLL**, i.e. ``-sum(log p)``, per row).

Also pairs (query, answer) strings under :class:`AugmentationSpec` using the same
forward/inverse grid transforms as TTA decoding.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any, Literal

from layers.layer_0_core.level_0 import get_torch

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    AugmentationSpec,
    apply_augmentation,
    invert_augmentation,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import ArcQwenGridChatFormatter

Grid = list[list[int]]

AggregateMode = Literal["sum", "mean", "min", "none"]


def _resolve_pad_id(tokenizer: Any, pad_id: int | None) -> int:
    if pad_id is not None:
        return int(pad_id)
    pid = getattr(tokenizer, "pad_token_id", None)
    if pid is None:
        return 13
    return int(pid)


def calc_scores(
    queries: list[str],
    answers: list[str],
    tokenizer: Any,
    model: Any,
    *,
    pad_id: int | None = None,
) -> list[float]:
    """Batched teacher-forced NLL per row (reference ``calc_scores``).

    Each returned value is ``-sum_t log p(answer_t | prefix)`` on the forced answer
    tokens (higher = worse). This matches the notebook implementation byte-for-byte
    in structure (padding, ``use_cache=True``, CPU ``log_softmax``, slice indices).
    """
    if len(queries) != len(answers):
        raise ValueError(f"queries ({len(queries)}) and answers ({len(answers)}) must have the same length.")
    torch = get_torch()
    device = next(model.parameters()).device

    batch_query_tokens: list[list[int]] = []
    batch_answer_tokens: list[list[int]] = []
    batch_tokens: list[list[int]] = []
    batch_lengths: list[int] = []
    for query, answer in zip(queries, answers):
        qt = tokenizer.encode(query)
        at = tokenizer.encode(answer)
        tokens = qt + at
        batch_query_tokens.append(qt)
        batch_answer_tokens.append(at)
        batch_tokens.append(tokens)
        batch_lengths.append(len(tokens))
    if not batch_lengths:
        return []

    pad = _resolve_pad_id(tokenizer, pad_id)
    max_len = max(batch_lengths)
    padded_tokens = [tokens + [pad] * (max_len - len(tokens)) for tokens in batch_tokens]
    input_ids = torch.tensor(padded_tokens, device=device, dtype=torch.long)
    with torch.no_grad():
        outputs = model(input_ids=input_ids, return_dict=True, use_cache=True)
    batch_logits = outputs.logits.float().cpu().log_softmax(-1)

    result: list[float] = []
    for logits, query_tokens, answer_tokens in zip(batch_logits, batch_query_tokens, batch_answer_tokens):
        query_length = len(query_tokens)
        alen = len(answer_tokens)
        if alen == 0:
            result.append(0.0)
            continue
        answer_logits = logits[query_length - 1 : query_length - 1 + alen]
        idx = torch.arange(alen, dtype=torch.long)
        toks = torch.tensor(answer_tokens, dtype=torch.long)
        answer_score = answer_logits[idx, toks].sum()
        result.append(float(-answer_score.item()))
    return result


def calc_scores_chunked(
    queries: list[str],
    answers: list[str],
    tokenizer: Any,
    model: Any,
    *,
    chunk_size: int,
    pad_id: int | None = None,
) -> list[float]:
    """Run :func:`calc_scores` in fixed-size chunks and **concatenate** results (notebook micro-batching)."""
    if chunk_size < 1:
        raise ValueError("chunk_size must be >= 1.")
    out: list[float] = []
    n = len(queries)
    for i in range(0, n, chunk_size):
        out.extend(
            calc_scores(
                queries[i : i + chunk_size],
                answers[i : i + chunk_size],
                tokenizer,
                model,
                pad_id=pad_id,
            )
        )
    return out


def concat_calc_score_batches(batch_results: Sequence[Sequence[float]]) -> list[float]:
    """Flatten multiple :func:`calc_scores` outputs in order (same as ``scores_a + scores_b`` in the notebook)."""
    out: list[float] = []
    for part in batch_results:
        out.extend(float(x) for x in part)
    return out


def aggregate_scores_across_augmentations(
    scores: Sequence[float],
    *,
    mode: Literal["sum", "mean", "min"],
) -> float:
    """Combine per-augmentation NLLs into one scalar (for ranking / logging)."""
    seq = [float(x) for x in scores]
    if not seq:
        raise ValueError("scores must be non-empty.")
    if mode == "sum":
        return float(sum(seq))
    if mode == "mean":
        return float(sum(seq) / len(seq))
    if mode == "min":
        return float(min(seq))
    raise ValueError(f"Unknown mode={mode!r}.")


def format_augmented_query_reply_strings(
    formatter: ArcQwenGridChatFormatter,
    input_grid: Grid,
    candidate_grid: Grid,
    spec: AugmentationSpec,
) -> tuple[str, str]:
    """Apply ``spec`` to both grids, then build Qwen chat query + reply strings for scoring."""
    aug_in = apply_augmentation(input_grid, spec)
    aug_out = apply_augmentation(candidate_grid, spec)
    q = formatter.fmt_query_from_input_grid(aug_in)
    a = formatter.fmt_reply_from_output_grid(aug_out)
    return q, a


def format_augmented_query_reply_batch(
    formatter: ArcQwenGridChatFormatter,
    input_grid: Grid,
    candidate_grid: Grid,
    specs: Sequence[AugmentationSpec],
) -> tuple[list[str], list[str]]:
    """Build parallel ``queries`` / ``answers`` lists for :func:`calc_scores`."""
    queries: list[str] = []
    answers: list[str] = []
    for spec in specs:
        q, a = format_augmented_query_reply_strings(formatter, input_grid, candidate_grid, spec)
        queries.append(q)
        answers.append(a)
    return queries, answers


def invert_candidate_grid(grid: Grid, spec: AugmentationSpec) -> Grid:
    """Map a grid from augmented space back to the original layout (thin wrapper over :func:`invert_augmentation`)."""
    return invert_augmentation(grid, spec)


def calc_scores_under_augmentations(
    model: Any,
    tokenizer: Any,
    formatter: ArcQwenGridChatFormatter,
    input_grid: Grid,
    candidate_grid: Grid,
    specs: Sequence[AugmentationSpec],
    *,
    pad_id: int | None = None,
    chunk_size: int | None = None,
    aggregate: AggregateMode = "none",
) -> list[float] | float:
    """Score ``candidate_grid`` under each augmentation in **augmented** prompt space (reference TTA pattern).

    Returns one NLL per spec, or a single aggregated value when ``aggregate`` is not ``none``.
    """
    queries, answers = format_augmented_query_reply_batch(formatter, input_grid, candidate_grid, specs)
    if chunk_size is not None:
        nlls = calc_scores_chunked(queries, answers, tokenizer, model, chunk_size=int(chunk_size), pad_id=pad_id)
    else:
        nlls = calc_scores(queries, answers, tokenizer, model, pad_id=pad_id)
    if aggregate == "none":
        return nlls
    return aggregate_scores_across_augmentations(nlls, mode=aggregate)


__all__ = [
    "calc_scores",
    "calc_scores_chunked",
    "concat_calc_score_batches",
    "aggregate_scores_across_augmentations",
    "format_augmented_query_reply_strings",
    "format_augmented_query_reply_batch",
    "invert_candidate_grid",
    "calc_scores_under_augmentations",
]
