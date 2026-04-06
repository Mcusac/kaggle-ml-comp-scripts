"""Local LB-style scoring: two attempts per test, partial credit across tests."""

from __future__ import annotations

from typing import Any

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.arc_grids_equal import (
    arc_grids_equal,
)


def eval_score_submission_two_attempts(
    replies: dict[str, list[Any]],
    submission: dict[str, Any],
) -> float:
    """Match reference ``ArcDataset.validate_submission`` weighting.

    Args:
        replies: ``task_id -> list of truth grids`` (one per test index).
        submission: competition-format ``task_id -> [ {attempt_1, attempt_2}, ... ]``.
    """
    score = 0.0
    for k, v in replies.items():
        if k not in submission:
            continue
        if not isinstance(v, list):
            continue
        sub = submission[k]
        if not isinstance(sub, list):
            continue
        for i, r in enumerate(v):
            if i >= len(sub):
                break
            item = sub[i]
            if not isinstance(item, dict):
                continue
            for attempt in ("attempt_1", "attempt_2"):
                if attempt not in item:
                    continue
                if arc_grids_equal(r, item[attempt]):
                    score += 1.0 / float(len(v))
                    break
    return float(score)


def eval_count_tasks(challenges: dict[str, Any]) -> int:
    return len(challenges) if isinstance(challenges, dict) else 0
