"""Per-task Unsloth LoRA adaptation runner (NVARC reference training loop)."""

from layers.layer_1_competition.level_0_infra.level_0 import (
    resolve_collator_token_ids,
    restore_peft_adapter_state_dict,
)
from layers.layer_1_competition.level_0_infra.level_4 import unsloth_train_completion_lm

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    ArcQwenGridChatFormatter,
)

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3.lm_task_adaptation.training_rows import (
    build_task_training_rows,
)


def run_unsloth_task_adaptation(
    *,
    model,
    tokenizer,
    default_adapter_state,
    task_payload,
    budget_expired,
    adaptation,
    max_seq_length,
):
    if budget_expired():
        return {"status": "skipped_budget"}, model

    restore_peft_adapter_state_dict(model, default_adapter_state)

    formatter = ArcQwenGridChatFormatter(tokenizer=tokenizer)

    rows = build_task_training_rows(
        task_payload,
        formatter,
        n_augmentations=adaptation.n_training_augmentations,
        augment_seed=adaptation.training_augment_seed,
        max_seq_length=max_seq_length,
    )

    if not rows:
        return {"status": "skipped"}, model

    user_id, assistant_id, eos_id = resolve_collator_token_ids(
        tokenizer,
        formatter,
    )

    model = unsloth_train_completion_lm(
        model=model,
        tokenizer=tokenizer,
        rows=rows,
        user_token_id=user_id,
        assistant_token_id=assistant_id,
        eos_token_id=eos_id,
        max_seq_length=max_seq_length,
        per_device_train_batch_size=adaptation.batch_size,
        gradient_accumulation_steps=adaptation.gradient_accumulation_steps,
        num_train_epochs=adaptation.num_train_epochs,
        learning_rate=adaptation.learning_rate,
    )

    return {"status": "ok", "num_rows": len(rows)}, model
