"""Logit-driven beam DFS with KV cache (NVARC ``turbo_dfs`` / ``inference_turbo_dfs``)."""

from __future__ import annotations

import time
from collections import defaultdict
from typing import Any, Dict, List, Sequence, Tuple

from layers.layer_0_core.level_0 import get_torch

_torch = get_torch()

# Preset token-id table for the ported NVARC notebook solver (model-specific); not ARC grid semantics.
NVARC_QWEN_GRID_SOLVER_TOKEN_VOCAB: dict[str, int] = {
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
    "<|im_end|>": 15,
}
DEFAULT_TURBO_DFS_ALLOWED_TOKEN_IDS: tuple[int, ...] = tuple(NVARC_QWEN_GRID_SOLVER_TOKEN_VOCAB.values())
TURBO_DFS_DEFAULT_PAD_ID: int = 13
TURBO_DFS_DEFAULT_EOS_ID: int = 15
TURBO_DFS_DEFAULT_INNER_LOOP_WALL_SEC: float = 540.0

TurboSuffixes = Dict[int, List[Tuple[float, List[int]]]]


def turbo_dfs(
    model: Any,
    logits: Any,
    max_new_tokens: int,
    max_score: float,
    scores: Sequence[float],
    pos: int,
    cache: Any,
    start_time: float,
    end_time: float,
    *,
    arc_tokens: Sequence[int] | None = None,
    pad_id: int = TURBO_DFS_DEFAULT_PAD_ID,
    eos_id: int = TURBO_DFS_DEFAULT_EOS_ID,
    inner_loop_wall_sec: float = TURBO_DFS_DEFAULT_INNER_LOOP_WALL_SEC,
) -> TurboSuffixes:
    if arc_tokens is None:
        arc_tokens = DEFAULT_TURBO_DFS_ALLOWED_TOKEN_IDS
    allowed = tuple(int(t) for t in arc_tokens)

    n = logits.size(0)
    if len(scores) != n:
        raise ValueError(f"scores length {len(scores)} must equal logits batch dimension {n}")

    nll = _torch.tensor(list(scores), dtype=_torch.float32, device="cpu").view(n, 1) - logits.float().cpu().log_softmax(
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
            input_ids=_torch.tensor(batch_tokens, device=model.device, dtype=_torch.long).view(-1, 1),
            position_ids=_torch.full((n, 1), int(pos), device=model.device),
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


@_torch.no_grad()
def inference_turbo_dfs(
    model: Any,
    prefix_tokens: Sequence[int],
    max_new_tokens: int,
    max_score: float,
    end_time: float,
    *,
    inner_loop_wall_sec: float = TURBO_DFS_DEFAULT_INNER_LOOP_WALL_SEC,
    arc_tokens: Sequence[int] | None = None,
    pad_id: int = TURBO_DFS_DEFAULT_PAD_ID,
    eos_id: int = TURBO_DFS_DEFAULT_EOS_ID,
) -> List[Tuple[int, List[Tuple[float, List[int]]]]]:
    if arc_tokens is None:
        arc_tokens = DEFAULT_TURBO_DFS_ALLOWED_TOKEN_IDS

    input_ids = _torch.as_tensor(list(prefix_tokens), device=model.device, dtype=_torch.long)
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


__all__ = [
    "DEFAULT_TURBO_DFS_ALLOWED_TOKEN_IDS",
    "NVARC_QWEN_GRID_SOLVER_TOKEN_VOCAB",
    "TURBO_DFS_DEFAULT_EOS_ID",
    "TURBO_DFS_DEFAULT_INNER_LOOP_WALL_SEC",
    "TURBO_DFS_DEFAULT_PAD_ID",
    "TurboSuffixes",
    "inference_turbo_dfs",
    "turbo_dfs",
]
