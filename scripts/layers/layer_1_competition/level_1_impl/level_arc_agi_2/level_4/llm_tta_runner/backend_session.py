"""LM backend bring-up and task-scoped cleanup for LLM-TTA DFS orchestration."""

from typing import Any, Callable, Mapping

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    ArcLmAdaptationConfig,
    LlmTtaDfsConfig,
    run_task_adaptation,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    per_task_adaptation_should_run,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2 import (
    ArcLmBackendConfig,
    build_lm_backend,
)



logger = get_logger(__name__)


def build_lm_backend(
    config: LlmTtaDfsConfig,
    task_payload: Mapping[str, Any] | None,
    budget_expired: Callable[[], bool],
) -> tuple[dict[str, Any], Any]:
    backend_cfg = ArcLmBackendConfig(
        model_path=str(config.model_path),
        lora_path=config.lora_path,
        attention_mode=str(config.runtime_attention_mode or "auto"),
        disable_compile=bool(config.runtime_disable_compile),
        seed=int(config.seed or 0),
    )
    backend = build_lm_backend(backend_cfg)
    backend.load()
    if per_task_adaptation_should_run(config):
        adapt_cfg = ArcLmAdaptationConfig(
            steps=int(config.adapt_steps or 0),
            batch_size=max(1, int(config.adapt_batch_size or 1)),
            gradient_accumulation_steps=max(1, int(config.adapt_gradient_accumulation_steps or 1)),
            disabled=False,
        )
        adapt_meta = run_task_adaptation(
            backend=backend,
            task_payload=task_payload if isinstance(task_payload, dict) else {},
            cfg=adapt_cfg,
            budget_expired=budget_expired,
        )
    else:
        adapt_meta = {"status": "skipped", "reason": "per_task_adaptation_off", "steps_ran": 0}
    return {
        "backend": backend.backend_name(),
        "adaptation": adapt_meta,
    }, backend


def restore_adapter_safely(lm_backend: Any) -> None:
    """Task-scoped adapter cleanup; swallows and logs errors to match prior behavior."""
    if lm_backend is None:
        return
    try:
        lm_backend.restore_base_adapter_after_task()
    except Exception as e:
        logger.warning("⚠️ restore_base_adapter_after_task failed (task-scoped cleanup): %s", e)
