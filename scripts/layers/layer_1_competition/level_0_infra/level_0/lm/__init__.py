"""Auto-generated package exports."""


from .attention_patchers import (
    install_repeat_interleave_attention,
    install_sdpa_attention,
)

from .collator_token_ids import resolve_collator_token_ids

from .completion_collator import (
    QwenDataCollatorForCompletionOnlyLM,
    REFERENCE_ASSISTANT_TOKEN_ID,
    REFERENCE_EOS_ID,
    REFERENCE_USER_TOKEN_ID,
)

from .ddp_utils import ddp_safe_loss

from .llm_tta_config import (
    LlmTtaDfsConfig,
    validate_llm_tta_dfs_config,
)

from .llm_tta_grid_shape import (
    Grid,
    empty_grid_like,
    llm_tta_augment_seed,
    llm_tta_grid_hw,
)

from .lm_adaptation import (
    LmAdaptationConfig,
    run_task_adaptation,
)

from .lm_budget import (
    ArcLmBudget,
    ArcLmRuntimeProfile,
    apply_runtime_profile,
    build_budget,
)

from .nll_scoring import (
    AggregateMode,
    Grid,
    aggregate_scores_across_augmentations,
    calc_scores,
    calc_scores_chunked,
    concat_calc_score_batches,
    eval_teacher_forced_neg_sum_logprob,
    eval_teacher_forced_neg_sum_logprob_batch,
    resolve_pad_id,
)

from .peft_bindings import (
    get_peft_model_state_dict,
    peft_module,
    set_peft_model_state_dict,
)

from .peft_defaults import (
    COMMON_PEFT_PARAMS,
    COMMON_TRAIN_ARGS,
)

from .tokenizer_utils import (
    resolve_digit_token_ids,
    resolve_newline_token_id,
    resolve_turbo_eos_id,
    resolve_turbo_token_table,
    token_id_for_single_text,
)

from .torch_utils import (
    load_adapter_state_dict,
    logger,
    torch_dtype_from_config,
    unsloth_available,
)

try:
    from .unsloth_trainers import (
        UnslothFixedTrainer,
        UnslothV2FixedTrainer,
    )
except ImportError:
    _unsloth_trainer_exports: tuple[str, ...] = ()
else:
    _unsloth_trainer_exports = ("UnslothFixedTrainer", "UnslothV2FixedTrainer")

__all__ = [
    "AggregateMode",
    "ArcLmBudget",
    "ArcLmRuntimeProfile",
    "COMMON_PEFT_PARAMS",
    "COMMON_TRAIN_ARGS",
    "Grid",
    "get_peft_model_state_dict",
    "install_repeat_interleave_attention",
    "install_sdpa_attention",
    "LlmTtaDfsConfig",
    "LmAdaptationConfig",
    "QwenDataCollatorForCompletionOnlyLM",
    "REFERENCE_ASSISTANT_TOKEN_ID",
    "REFERENCE_EOS_ID",
    "REFERENCE_USER_TOKEN_ID",
    "aggregate_scores_across_augmentations",
    "apply_runtime_profile",
    "build_budget",
    "calc_scores",
    "calc_scores_chunked",
    "concat_calc_score_batches",
    "ddp_safe_loss",
    "empty_grid_like",
    "eval_teacher_forced_neg_sum_logprob",
    "eval_teacher_forced_neg_sum_logprob_batch",
    "llm_tta_augment_seed",
    "llm_tta_grid_hw",
    "load_adapter_state_dict",
    "logger",
    "peft_module",
    "resolve_collator_token_ids",
    "resolve_digit_token_ids",
    "resolve_newline_token_id",
    "resolve_pad_id",
    "resolve_turbo_eos_id",
    "resolve_turbo_token_table",
    "run_task_adaptation",
    "set_peft_model_state_dict",
    "token_id_for_single_text",
    "torch_dtype_from_config",
    "unsloth_available",
    "validate_llm_tta_dfs_config",
    *list(_unsloth_trainer_exports),
]
