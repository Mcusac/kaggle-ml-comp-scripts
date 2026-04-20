"""Budget/timing/profile helpers for LLM-TTA DFS orchestration."""

import time

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    ArcLmBudget,
    ArcLmRuntimeProfile,
    LlmTtaDfsConfig,
)


def turbo_wall_end_time(budget: ArcLmBudget) -> float:
    """Map perf_counter deadlines in ``ArcLmBudget`` to ``time.time()`` for ``inference_turbo_dfs``."""
    now_pc = budget.now()
    remain: list[float] = []
    if budget.global_deadline_ts > 0.0:
        remain.append(float(budget.global_deadline_ts - now_pc))
    if budget.task_deadline_ts > 0.0:
        remain.append(float(budget.task_deadline_ts - now_pc))
    if budget.decode_deadline_ts > 0.0:
        remain.append(float(budget.decode_deadline_ts - now_pc))
    if not remain:
        return float(time.time()) + 86400.0
    return float(time.time()) + max(0.0, min(remain))


def build_runtime_profile(config: LlmTtaDfsConfig) -> ArcLmRuntimeProfile:
    return ArcLmRuntimeProfile(
        attention_mode=str(config.runtime_attention_mode or "auto"),
        disable_compile=bool(config.runtime_disable_compile),
        allocator_expandable_segments=bool(config.runtime_allocator_expandable_segments),
        allocator_max_split_size_mb=int(config.runtime_allocator_max_split_size_mb or 0),
    )


def per_task_adaptation_should_run(config: LlmTtaDfsConfig) -> bool:
    """NVARC-style fine-tune before decode when ``per_task_adaptation`` is on (explicit opt-in)."""
    if not bool(getattr(config, "per_task_adaptation", False)):
        return False
    if bool(config.adapt_disabled):
        return False
    return int(config.adapt_steps or 0) > 0
