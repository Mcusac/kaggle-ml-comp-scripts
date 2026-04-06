"""Per-task adaptation loop helpers for ARC LM mode."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ArcLmAdaptationConfig:
    steps: int = 0
    batch_size: int = 1
    gradient_accumulation_steps: int = 1
    disabled: bool = False


def run_task_adaptation(
    *,
    backend: Any,
    task_payload: dict[str, Any],
    cfg: ArcLmAdaptationConfig,
    budget_expired: callable,
) -> dict[str, Any]:
    """Run a bounded adaptation loop; backend decides actual update semantics."""
    if bool(cfg.disabled):
        return {"status": "skipped", "reason": "adapt_disabled", "steps_ran": 0}
    total = max(0, int(cfg.steps or 0))
    if total <= 0:
        return {"status": "skipped", "reason": "zero_steps", "steps_ran": 0}
    steps_ran = 0
    for _ in range(total):
        if budget_expired():
            return {"status": "stopped_budget", "steps_ran": steps_ran}
        backend.adapt_for_task(task_payload, budget_expired)
        steps_ran += 1
    return {"status": "ok", "steps_ran": steps_ran}
