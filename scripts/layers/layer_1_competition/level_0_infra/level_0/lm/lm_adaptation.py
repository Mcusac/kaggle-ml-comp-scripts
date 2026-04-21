"""Per-task adaptation loop helpers for LM backends."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class LmAdaptationConfig:
    steps: int = 0
    batch_size: int = 1
    gradient_accumulation_steps: int = 1
    disabled: bool = False
    num_train_epochs: int = 1
    learning_rate: float = 5e-5
    n_training_augmentations: int = 16
    training_augment_seed: int = 1
    warmup_steps: int = 0
    warmup_ratio: float = 0.1
    max_grad_norm: float = 1.0
    optim: str = "adamw_8bit"
    weight_decay: float = 0.0
    lr_scheduler_type: str = "cosine"


def run_task_adaptation(
    *,
    backend: Any,
    task_payload: dict[str, Any],
    cfg: LmAdaptationConfig,
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
        backend.adapt_for_task(task_payload, budget_expired, adaptation=cfg)
        steps_ran += 1
    return {"status": "ok", "steps_ran": steps_ran}