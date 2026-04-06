"""Trim ARC task ``train`` pairs until chat ``text`` fits a tokenizer length budget (reference ``cut_to_len``)."""

# FLAG: naming — optional rename to lm_token_budget_trim (or similar); deferred to reduce import churn.

from __future__ import annotations

import copy
from typing import Any, Mapping

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.lm_qwen_chat_format import (
    ArcQwenGridChatFormatter,
    arc_count_tokens,
)

Grid = list[list[int]]


def _train_pairs_for_fmt(train: list[Any]) -> list[dict[str, Grid]]:
    out: list[dict[str, Grid]] = []
    for x in train:
        if not isinstance(x, dict):
            continue
        gi = x.get("input")
        go = x.get("output")
        if isinstance(gi, list) and isinstance(go, list):
            out.append({"input": gi, "output": go})
    return out


def train_trim_task_train_pairs_to_token_budget(
    task: Mapping[str, Any],
    formatter: ArcQwenGridChatFormatter,
    *,
    max_len: int,
    from_end: bool = False,
) -> dict[str, Any]:
    """Return a deep-copied task with shortened ``train`` until ``fmt_train_block`` length <= ``max_len``.

    Drops from the front of ``train`` by default, or from the end when ``from_end`` is True.
    Stops when one pair remains or budget is met.
    """
    out = copy.deepcopy(dict(task))
    train = out.get("train")
    if not isinstance(train, list) or len(train) < 2:
        return out
    while len(train) >= 2:
        pairs = _train_pairs_for_fmt(train)
        text = formatter.fmt_train_block(pairs, last_is_challenge=False)
        if arc_count_tokens(formatter, text) <= int(max_len):
            break
        if from_end:
            train.pop()
        else:
            train.pop(0)
    out["train"] = train
    return out
