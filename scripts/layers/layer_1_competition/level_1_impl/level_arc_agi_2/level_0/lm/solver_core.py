from layers.layer_0_core.level_0 import get_torch

torch = get_torch()

# ---------------------------------------------------------------------------
# Shared PEFT params (identical in v1 + v2)
# ---------------------------------------------------------------------------

COMMON_PEFT_PARAMS = dict(
    r=256,
    target_modules=[
        "q_proj", "k_proj", "v_proj", "o_proj",
        "gate_proj", "up_proj", "down_proj",
        "embed_tokens", "lm_head",
    ],
    lora_alpha=32,
    lora_dropout=0.0,
    bias="none",
    use_gradient_checkpointing=False,
    random_state=42,
    use_rslora=True,
    loftq_config=None,
)


# ---------------------------------------------------------------------------
# Shared base train args (v1 + v2 derive from this)
# ---------------------------------------------------------------------------

COMMON_TRAIN_ARGS = dict(
    per_device_eval_batch_size=1,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=1,
    num_train_epochs=1,
    warmup_steps=0,
    warmup_ratio=0.1,
    max_grad_norm=1.0,
    learning_rate=5e-5,
    weight_decay=0.0,
    lr_scheduler_type="cosine",
    seed=42,
    report_to="none",
    save_strategy="no",
    eval_strategy="no",
    logging_strategy="no",
    bf16=False,
    fsdp="",
    ddp_find_unused_parameters=False,
    dataloader_num_workers=0,
    gradient_checkpointing=False,
)