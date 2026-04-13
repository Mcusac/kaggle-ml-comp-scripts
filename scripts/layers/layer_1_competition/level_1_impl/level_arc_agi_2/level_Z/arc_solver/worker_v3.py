"""
Solver v3 — entry point.

Characteristics vs v1/v2:
  - Env:       TORCH_COMPILE_DISABLE=1, UNSLOTH_USE_COMPILED=0  (set at import time)
  - Attention: memory-efficient SDPA + expand GQA  (patched at module level)
  - Loss:      vanilla CrossEntropyLoss, bypasses Unsloth compiled path entirely
  - Optimizer: adamw_torch,  fp16=True
  - Seq len:   4096
  - Model:     different Kaggle notebook path, attn_implementation="sdpa"
  - Batching:  single subkey per batch (maximises memory headroom)
  - Cleanup:   zeros gradients + empties cache after training; empties cache after each batch
"""

import os

# Must be set before any torch / unsloth import.
os.environ["TORCH_COMPILE_DISABLE"] = "1"
os.environ["UNSLOTH_USE_COMPILED"] = "0"

import torch

from .attention import install_sdpa_attention
from .config import WorkerConfig, build_batches_single
from .trainer import UnslothV3FixedTrainer
from .worker import worker_core

# Patch attention at module import time (v3 does this globally, not inside worker).
install_sdpa_attention()


# ---------------------------------------------------------------------------
# v3 config
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
    optim="adamw_torch",
    weight_decay=0.0,
    lr_scheduler_type="cosine",
    seed=42,
    report_to="none",
    save_strategy="no",
    eval_strategy="no",
    logging_strategy="no",
    fp16=True,
    bf16=False,
    fsdp="",
    ddp_find_unused_parameters=False,
    dataloader_num_workers=0,
    gradient_checkpointing=False,
)


def _post_peft_setup_v3(model):
    """Ensure training mode is active immediately after adapter attachment."""
    from unsloth import FastLanguageModel
    return FastLanguageModel.for_training(model)


def _post_train_cleanup_v3(model, trainer) -> None:
    """Zero gradients and flush cache before unwrapping — reduces peak VRAM."""
    model.zero_grad(set_to_none=True)
    torch.cuda.empty_cache()


def _post_batch_cleanup_v3(tokens, dfs_result) -> None:
    """Aggressively free DFS search tensors after each inference batch."""
    del tokens
    del dfs_result
    torch.cuda.empty_cache()


V3_CONFIG = WorkerConfig(
    model_name="/kaggle/input/notebooks/mirzamilanfarabi/qwen3-4b-grids15-sft139",
    max_seq_length=4096,
    model_load_kwargs=dict(
        dtype=torch.float16,
        attn_implementation="sdpa",
    ),
    peft_params=PEFT_PARAMS,
    train_args=TRAIN_ARGS,
    trainer_class=UnslothV3FixedTrainer,
    install_attention=None,          # already patched at module-import time above
    post_peft_setup=_post_peft_setup_v3,
    post_train_cleanup=_post_train_cleanup_v3,
    build_batches=build_batches_single,
    dir_outputs="/kaggle/tmp/inference_outputs",
    post_batch_cleanup=_post_batch_cleanup_v3,
    disable_amp_grad_scaler=False,   # v3 uses native fp16 via PyTorch — no need to disable
)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def worker(rank: int, queue, end_time: float) -> None:
    worker_core(rank, queue, end_time, V3_CONFIG)