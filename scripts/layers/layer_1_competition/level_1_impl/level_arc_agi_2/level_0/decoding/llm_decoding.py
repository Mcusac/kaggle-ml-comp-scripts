"""Reference NVARC ``turbo_dfs`` / ``inference_turbo_dfs`` (logit-driven beam + KV cache).

Ported from reference notebooks' ``arc_solver.py`` (e.g. ``nvarc-arc-2025-winning-solution-for-t4x2-gpu.ipynb``).
Used by ``ArcLmBackend.turbo_dfs_beams`` and ``llm_tta_runner`` (Phase 2).

Behavior (matches reference):
  - cumulative NLL: ``score_new = score_parent - log_softmax(logits)[token]``
  - expand only tokens in ``arc_tokens`` with ``score < max_score`` (pruning)
  - EOS token closes a beam without a depth step; non-EOS requires ``max_new_tokens > 1`` to recurse
  - batch step: pop lowest-NLL candidate per batch row; PAD / dead rows use ``PAD_ID`` and score ``1000``, excluded from ``num_alive_beams``
  - inner while-loop wall time: ``time.time() - start_time < inner_loop_wall_sec`` and ``time.time() < end_time`` (early stop)
  - ``max_new_tokens`` decrements each recurse (max depth control)
"""

import time

from collections import defaultdict
from typing import Any, Dict, List, Sequence, Tuple

from layers.layer_0_core.level_0 import get_torch

torch = get_torch()

# Reference ``arc_solver.py`` (token ids are model-specific; defaults match NVARC notebook)
REFERENCE_ARC_VOCAB: dict[str, int] = {
    "0": 0,
    "1": 1,
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "Ċ": 10,
    "<|redacted_im_end|>": 15,
}
REFERENCE_ARC_TOKENS: tuple[int, ...] = tuple(REFERENCE_ARC_VOCAB.values())
REFERENCE_USER_TOKEN_ID: int = 11
REFERENCE_ASSISTANT_TOKEN_ID: int = 12
REFERENCE_PAD_ID: int = 13
REFERENCE_EOS_ID: int = 15

# Reference hard-codes 540 seconds for the inner while-loop (in addition to ``end_time``).
REFERENCE_INNER_LOOP_WALL_SEC: float = 540.0

TurboSuffixes = Dict[int, List[Tuple[float, List[int]]]]


def turbo_dfs(
    model: Any,
    logits: torch.Tensor,
    max_new_tokens: int,
    max_score: float,
    scores: Sequence[float],
    pos: int,
    cache: Any,
    start_time: float,
    end_time: float,
    *,
    arc_tokens: Sequence[int] | None = None,
    pad_id: int = REFERENCE_PAD_ID,
    eos_id: int = REFERENCE_EOS_ID,
    inner_loop_wall_sec: float = REFERENCE_INNER_LOOP_WALL_SEC,
) -> TurboSuffixes:
    """Recursive logit-driven expansion with KV cache (same structure as reference ``turbo_dfs``).

    Args:
        model: HF / Unsloth causal LM; ``model.device`` and ``model(...)`` with ``past_key_values``.
        logits: Last-step logits, shape ``[batch, vocab_size]``.
        max_new_tokens: Remaining generation depth (reference decrements per step).
        max_score: Prune threshold on cumulative NLL (reference uses ``-log(0.2)``).
        scores: Parent cumulative NLL per batch row (length must equal ``logits.size(0)``).
        pos: ``position_ids`` value for the *current* single-token forward (reference passes ``pos`` then ``pos+1``).
        cache: ``past_key_values`` from the previous step (or ``None`` on first step inside recursion).
        start_time: ``time.time()`` anchor for inner-loop wall clock (reference sets this once in ``inference_turbo_dfs``).
        end_time: Absolute deadline; inner loop stops when ``time.time() >= end_time``.
        arc_tokens: Allowed token ids to expand (default: ``ALL`` from reference ARC vocab).
        pad_id: Padding id for dead batch slots in the batched forward (reference ``PAD_ID``).
        eos_id: End id (reference ``EOS_ID``).
        inner_loop_wall_sec: Inner ``while`` budget (reference ``540``).

    Returns:
        ``dict[batch_id, list[(score, token_ids)]]`` partial suffixes from *this* recursion level;
        caller prepends chosen tokens (reference inserts ``batch_tokens[batch_id]`` at front of suffix).
    """
    if arc_tokens is None:
        arc_tokens = REFERENCE_ARC_TOKENS
    allowed = tuple(int(t) for t in arc_tokens)

    n = logits.size(0)
    if len(scores) != n:
        raise ValueError(f"scores length {len(scores)} must equal logits batch dimension {n}")

    nll = torch.tensor(list(scores), dtype=torch.float32, device="cpu").view(n, 1) - logits.float().cpu().log_softmax(
        dim=-1
    )

    suffixes: dict[int, list[tuple[float, list[int]]]] = defaultdict(list)
    candidates: dict[int, list[tuple[float, int]]] = {i: [] for i in range(n)}

    for i in range(n):
        for t in allowed:
            score = float(nll[i, t].item())
            if score < float(max_score):
                if int(t) == int(eos_id):
                    suffixes[i].append((score, [int(t)]))
                elif int(max_new_tokens) > 1:
                    candidates[i].append((score, int(t)))

    for i in range(n):
        candidates[i] = sorted(candidates[i], key=lambda x: x[0])

    while (time.time() - start_time) < float(inner_loop_wall_sec) and time.time() < float(end_time):
        batch_tokens: list[int] = []
        batch_scores: list[float] = []
        num_alive_beams = 0

        for i in range(n):
            if len(candidates[i]) == 0:
                batch_tokens.append(int(pad_id))
                batch_scores.append(1000.0)
            else:
                score, t = candidates[i].pop(0)
                batch_tokens.append(int(t))
                batch_scores.append(float(score))
                num_alive_beams += 1

        if num_alive_beams == 0:
            break

        outputs = model(
            input_ids=torch.tensor(batch_tokens, device=model.device, dtype=torch.long).view(-1, 1),
            position_ids=torch.full((n, 1), int(pos), device=model.device),
            past_key_values=cache,
            return_dict=True,
            use_cache=True,
        )

        next_suffixes = turbo_dfs(
            model,
            outputs.logits[:, -1],
            int(max_new_tokens) - 1,
            float(max_score),
            batch_scores,
            int(pos) + 1,
            outputs.past_key_values,
            start_time,
            float(end_time),
            arc_tokens=allowed,
            pad_id=int(pad_id),
            eos_id=int(eos_id),
            inner_loop_wall_sec=float(inner_loop_wall_sec),
        )

        for batch_id, beams in next_suffixes.items():
            for score, suffix_tokens in beams:
                suffix_tokens.insert(0, batch_tokens[batch_id])
                suffixes[batch_id].append((float(score), suffix_tokens))

    return dict(suffixes)


@torch.no_grad()
def inference_turbo_dfs(
    model: Any,
    prefix_tokens: Sequence[int],
    max_new_tokens: int,
    max_score: float,
    end_time: float,
    *,
    inner_loop_wall_sec: float = REFERENCE_INNER_LOOP_WALL_SEC,
    arc_tokens: Sequence[int] | None = None,
    pad_id: int = REFERENCE_PAD_ID,
    eos_id: int = REFERENCE_EOS_ID,
) -> List[Tuple[int, List[Tuple[float, List[int]]]]]:
    """Run prefix forward once, then ``turbo_dfs`` (same structure as reference ``inference_turbo_dfs``).

    Reference passes ``prefix_tokens`` as a 1D tensor; HF causal LMs expect ``[batch, seq]``.
    We ``unsqueeze(0)`` when needed so ``logits.size(0)`` and ``scores`` stay consistent (batch = 1).
    """
    if arc_tokens is None:
        arc_tokens = REFERENCE_ARC_TOKENS

    input_ids = torch.as_tensor(list(prefix_tokens), device=model.device, dtype=torch.long)
    if input_ids.dim() == 1:
        input_ids = input_ids.unsqueeze(0)

    outputs = model(input_ids=input_ids, return_dict=True, use_cache=True)

    suffixes = turbo_dfs(
        model,
        outputs.logits[:, -1],
        int(max_new_tokens),
        float(max_score),
        [0.0] * int(input_ids.size(0)),
        int(input_ids.size(1)),
        outputs.past_key_values,
        time.time(),
        float(end_time),
        arc_tokens=arc_tokens,
        pad_id=int(pad_id),
        eos_id=int(eos_id),
        inner_loop_wall_sec=float(inner_loop_wall_sec),
    )

    result: list[tuple[int, list[tuple[float, list[int]]]]] = []
    for batch_id, beams in suffixes.items():
        sorted_beams = sorted(beams, key=lambda x: x[0])
        result.append((int(batch_id), sorted_beams))
    return result
