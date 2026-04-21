"""Batched teacher-forced NLL core (reference ``calc_scores`` + chunking/aggregation).

Copied from ARC-AGI-2 contest implementation for reuse by other LM contests.
"""

from collections.abc import Sequence
from typing import Any, Literal

from layers.layer_0_core.level_0 import get_torch

Grid = list[list[int]]

AggregateMode = Literal["sum", "mean", "min", "none"]


def resolve_pad_id(tokenizer: Any, pad_id: int | None) -> int:
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

    pad = resolve_pad_id(tokenizer, pad_id)
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


def eval_teacher_forced_neg_sum_logprob(
    *,
    model: Any,
    tokenizer: Any,
    query_text: str,
    answer_text: str,
    device: Any,
) -> float | None:
    """Negative sum of log-probs on ``answer_text`` tokens (lower = better)."""
    torch = get_torch()
    query_tokens = tokenizer.encode(query_text)
    answer_tokens = tokenizer.encode(answer_text)
    tokens = query_tokens + answer_tokens
    if not tokens:
        return None
    input_ids = torch.tensor([tokens], device=device, dtype=torch.long)
    with torch.no_grad():
        out = model(input_ids=input_ids, return_dict=True)
    logits = out.logits.float()
    logp = torch.nn.functional.log_softmax(logits[:, :-1, :], dim=-1)
    labels = input_ids[:, 1:]
    answer_start = max(0, len(query_tokens) - 1)
    total = 0.0
    for t, lab in enumerate(labels[0]):
        if t < answer_start:
            continue
        lab_i = int(lab.item())
        if 0 <= lab_i < logp.shape[-1]:
            total -= float(logp[0, t, lab_i].item())
    return float(total)


def eval_teacher_forced_neg_sum_logprob_batch(
    *,
    model: Any,
    tokenizer: Any,
    queries: list[str],
    answers: list[str],
    device: Any,
) -> list[float | None]:
    """Batched teacher-forced scores (padding pattern aligned with :func:`calc_scores`)."""
    torch = get_torch()
    batch_query_tokens: list[list[int]] = []
    batch_answer_tokens: list[list[int]] = []
    batch_tokens: list[list[int]] = []
    batch_lengths: list[int] = []
    for query, answer in zip(queries, answers):
        qt = tokenizer.encode(query)
        at = tokenizer.encode(answer)
        seq = qt + at
        batch_query_tokens.append(qt)
        batch_answer_tokens.append(at)
        batch_tokens.append(seq)
        batch_lengths.append(len(seq))
    if not batch_lengths:
        return []
    max_len = max(batch_lengths)
    pad_id = getattr(tokenizer, "pad_token_id", None)
    if pad_id is None:
        pad_id = 0
    padded: list[list[int]] = []
    for seq in batch_tokens:
        padded.append(seq + [int(pad_id)] * (max_len - len(seq)))
    input_ids = torch.tensor(padded, device=device, dtype=torch.long)
    with torch.no_grad():
        out = model(input_ids=input_ids, return_dict=True)
    batch_logits = out.logits.float()
    logp = torch.nn.functional.log_softmax(batch_logits, dim=-1)
    result: list[float | None] = []
    for row, qt, at in zip(range(input_ids.size(0)), batch_query_tokens, batch_answer_tokens):
        qlen = len(qt)
        alen = len(at)
        if alen == 0:
            result.append(0.0)
            continue
        total = 0.0
        for t in range(alen):
            pos = qlen - 1 + t
            if pos < 0 or pos >= logp.size(1):
                break
            tid = int(at[t])
            if 0 <= tid < logp.size(-1):
                total -= float(logp[row, pos, tid].item())
        result.append(float(total))
    return result

