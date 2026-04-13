"""
Beam-search decoding and scoring utilities shared across all solver variants.

  turbo_dfs            — recursive depth-first beam search over ARC token space.
  inference_turbo_dfs  — entry point: encodes prefix, runs turbo_dfs, returns sorted beams.
  calc_scores          — batched log-likelihood scoring of (query, answer) pairs.
"""

import time

from collections import defaultdict

from layers.layer_0_core.level_0 import get_torch
from .constants import ARC_TOKENS, EOS_ID, PAD_ID

torch = get_torch()


def turbo_dfs(
    model,
    logits,
    max_new_tokens: int,
    max_score: float,
    scores: list,
    pos: int,
    cache,
    start_time: float,
    end_time: float,
) -> dict:
    """
    Recursive DFS beam search restricted to ARC tokens.

    Returns a dict mapping batch index → list of (score, token_list) beams.
    """
    n = logits.size(0)
    nll = torch.tensor(scores, dtype=torch.float32).view(n, 1) - logits.float().cpu().log_softmax(-1)

    suffixes: dict = defaultdict(list)
    candidates: dict = {i: [] for i in range(n)}

    for i in range(n):
        for t in ARC_TOKENS:
            score = nll[i, t].item()
            if score < max_score:
                if t == EOS_ID:
                    suffixes[i].append((score, [t]))
                elif max_new_tokens > 1:
                    candidates[i].append((score, t))
        candidates[i].sort(key=lambda x: x[0])

    while time.time() - start_time < 540 and time.time() < end_time:
        batch_tokens = []
        batch_scores = []
        num_alive_beams = 0

        for i in range(n):
            if not candidates[i]:
                batch_tokens.append(PAD_ID)
                batch_scores.append(1000)
            else:
                score, t = candidates[i].pop(0)
                batch_tokens.append(t)
                batch_scores.append(score)
                num_alive_beams += 1

        if num_alive_beams == 0:
            break

        outputs = model(
            input_ids=torch.tensor(batch_tokens, device=model.device, dtype=torch.long).view(-1, 1),
            position_ids=torch.full((n, 1), pos, device=model.device),
            past_key_values=cache,
            return_dict=True,
            use_cache=True,
        )

        next_suffixes = turbo_dfs(
            model,
            logits=outputs.logits[:, -1],
            max_new_tokens=max_new_tokens - 1,
            max_score=max_score,
            scores=batch_scores,
            pos=pos + 1,
            cache=outputs.past_key_values,
            start_time=start_time,
            end_time=end_time,
        )

        # Explicit delete prevents recursion-level tensor accumulation (v3 fix, safe for all)
        del outputs

        for batch_id, beams in next_suffixes.items():
            for score, suffix_tokens in beams:
                suffix_tokens.insert(0, batch_tokens[batch_id])
                suffixes[batch_id].append((score, suffix_tokens))

    return suffixes


@torch.no_grad()
def inference_turbo_dfs(model, prefix_tokens, max_new_tokens: int, max_score: float, end_time: float):
    """Run turbo_dfs from a batch of encoded prefix token sequences."""
    input_ids = torch.tensor(prefix_tokens, device=model.device, dtype=torch.long)
    outputs = model(input_ids=input_ids, return_dict=True, use_cache=True)
    suffixes = turbo_dfs(
        model,
        logits=outputs.logits[:, -1],
        max_new_tokens=max_new_tokens,
        max_score=max_score,
        scores=[0.0] * input_ids.size(0),
        pos=input_ids.size(1),
        cache=outputs.past_key_values,
        start_time=time.time(),
        end_time=end_time,
    )
    return [(batch_id, sorted(beams, key=lambda x: x[0])) for batch_id, beams in suffixes.items()]


@torch.no_grad()
def calc_scores(queries: list, answers: list, tokenizer, model) -> list:
    """
    Compute per-answer negative log-likelihood scores for a batch of (query, answer) pairs.
    Lower score = higher likelihood.
    """
    batch_query_tokens, batch_answer_tokens, batch_tokens, batch_lengths = [], [], [], []

    for query, answer in zip(queries, answers):
        q_toks = tokenizer.encode(query)
        a_toks = tokenizer.encode(answer)
        batch_query_tokens.append(q_toks)
        batch_answer_tokens.append(a_toks)
        batch_tokens.append(q_toks + a_toks)
        batch_lengths.append(len(q_toks) + len(a_toks))

    max_len = max(batch_lengths)
    padded_tokens = [toks + [PAD_ID] * (max_len - len(toks)) for toks in batch_tokens]

    input_ids = torch.tensor(padded_tokens, device=model.device, dtype=torch.long)
    outputs = model(input_ids=input_ids, return_dict=True, use_cache=True)
    batch_logits = outputs.logits.float().cpu().log_softmax(-1)

    result = []
    for logits, q_toks, a_toks in zip(batch_logits, batch_query_tokens, batch_answer_tokens):
        q_len = len(q_toks)
        answer_logits = logits[q_len - 1 : q_len - 1 + len(a_toks)]
        answer_score = answer_logits[torch.arange(len(a_toks)), a_toks].sum()
        result.append(-answer_score.item())

    return result