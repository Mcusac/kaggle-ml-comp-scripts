"""Completion-only label spans for causal LM (list[int] API, ignores index ``mask_id``)."""

from __future__ import annotations


def train_build_completion_only_labels(
    input_ids: list[int],
    assistant_spans: list[tuple[int, int]],
    *,
    mask_id: int = -100,
) -> list[int]:
    """Return label list: ``mask_id`` everywhere except ``assistant_spans`` (inclusive start, exclusive end)."""
    if mask_id == 0:
        raise ValueError("mask_id must not be 0 (ambiguous with token id 0).")
    n = len(input_ids)
    labels = [mask_id] * n
    for start, end in assistant_spans:
        a = max(0, int(start))
        b = min(n, int(end))
        if a >= b:
            continue
        for i in range(a, b):
            labels[i] = int(input_ids[i])
    return labels
