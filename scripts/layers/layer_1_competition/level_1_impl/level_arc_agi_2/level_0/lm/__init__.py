"""Auto-generated package exports."""


from .lm_adaptation import (
    ArcLmAdaptationConfig,
    run_task_adaptation,
)

from .lm_attention_patcher_repeat_interleave import (
    install_repeat_interleave_attention,
    torch,
)

from .lm_attention_patcher_sdpa import install_sdpa_attention

from .solver_core import (
    COMMON_PEFT_PARAMS,
    COMMON_TRAIN_ARGS,
    torch,
)

from .trainer_ddp_loss import ddp_safe_loss

__all__ = [
    "ArcLmAdaptationConfig",
    "COMMON_PEFT_PARAMS",
    "COMMON_TRAIN_ARGS",
    "ddp_safe_loss",
    "install_repeat_interleave_attention",
    "install_sdpa_attention",
    "run_task_adaptation",
    "torch",
]
