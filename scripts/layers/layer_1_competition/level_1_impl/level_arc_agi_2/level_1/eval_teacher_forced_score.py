"""Optional teacher-forced sequence score for causal LMs (torch only)."""

from __future__ import annotations

from typing import Any


def eval_teacher_forced_neg_sum_logprob(
    *,
    model: Any,
    tokenizer: Any,
    query_text: str,
    answer_text: str,
    device: Any,
) -> float | None:
    """Return negative sum of log-probs on ``answer_text`` tokens (lower = better).

    Returns ``None`` if torch/transformers path fails.
    """
    try:
        import torch
    except Exception:
        return None
    try:
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
    except Exception:
        return None


def eval_teacher_forced_neg_sum_logprob_batch(
    *,
    model: Any,
    tokenizer: Any,
    queries: list[str],
    answers: list[str],
    device: Any,
) -> list[float | None]:
    """Batched teacher-forced scores (reference ``calc_scores`` padding pattern).

    Returns per-row negative sum log-prob on answer tokens, or ``None`` on failure.
    """
    try:
        import torch
    except Exception:
        return [None] * len(queries)
    if len(queries) != len(answers):
        return [None] * len(queries)
    try:
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
    except Exception:
        return [None] * len(queries)
