"""
Solver v1 — entry point.

Characteristics:
  - Attention: manual GQA via repeat_interleave  (patched inside worker startup)
  - Loss:      label_smoother path with Unsloth model detection
  - Optimizer: adamw_8bit,  fp16=False,  half_precision_backend=cpu_amp
  - Seq len:   8192
  - Batching:  grouped-4 subkeys per batch
  - AMP grad scaler disabled (monkey-patched)
"""

import torch

from .attention import install_repeat_interleave_attention
from .config import WorkerConfig, build_batches_grouped
from .trainer import UnslothFixedTrainer
from .worker import worker_core

# ---------------------------------------------------------------------------
# v1 config
# ---------------------------------------------------------------------------

PEFT_PARAMS = dict(
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

TRAIN_ARGS = dict(
    per_device_eval_batch_size=1,
    per_device_train_batch_size=1,
    gradient_accumulation_steps=1,
    num_train_epochs=1,
    warmup_steps=0,
    warmup_ratio=0.1,
    max_grad_norm=1.0,
    learning_rate=5e-5,
    optim="adamw_8bit",
    weight_decay=0.0,
    lr_scheduler_type="cosine",
    seed=42,
    report_to="none",
    save_strategy="no",
    eval_strategy="no",
    logging_strategy="no",
    fp16=False,
    bf16=False,
    fsdp="",
    ddp_find_unused_parameters=False,
    dataloader_num_workers=0,
    gradient_checkpointing=False,
    half_precision_backend="cpu_amp",
    no_cuda=False,
)


def _post_peft_setup_v1(model):
    model.config._attn_implementation = "eager"
    return model


V1_CONFIG = WorkerConfig(
    model_name="/kaggle/input/qwen3_4b_grids15_sft139/transformers/bfloat16/1",
    max_seq_length=8192,
    model_load_kwargs=dict(
        dtype=torch.float16,
        attn_implementation="eager",
    ),
    peft_params=PEFT_PARAMS,
    train_args=TRAIN_ARGS,
    trainer_class=UnslothFixedTrainer,
    install_attention=install_repeat_interleave_attention,
    post_peft_setup=_post_peft_setup_v1,
    build_batches=build_batches_grouped,
    dir_outputs="/kaggle/inference_outputs",
    disable_amp_grad_scaler=True,
)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def worker(rank: int, queue, end_time: float) -> None:
    worker_core(rank, queue, end_time, V1_CONFIG)