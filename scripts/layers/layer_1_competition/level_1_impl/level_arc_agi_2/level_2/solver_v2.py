"""
Solver v2 — entry point.
"""

import os

os.environ["TORCH_COMPILE_DISABLE"] = "1"
os.environ["UNSLOTH_USE_COMPILED"] = "0"

from layers.layer_0_core.level_0 import get_torch

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    install_sdpa_attention,
    UnslothV2FixedTrainer,
    COMMON_PEFT_PARAMS, 
    COMMON_TRAIN_ARGS
)

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    WorkerConfig,
    build_batches_single,
    worker_core,
)

torch = get_torch()

install_sdpa_attention()

TRAIN_ARGS = dict(
    **COMMON_TRAIN_ARGS,
    optim="adamw_torch",
    fp16=True,
)


def _post_peft_setup_v2(model):
    from unsloth import FastLanguageModel
    return FastLanguageModel.for_training(model)


def _post_train_cleanup_v2(model, trainer) -> None:
    model.zero_grad(set_to_none=True)
    torch.cuda.empty_cache()


def _post_batch_cleanup_v2(tokens, dfs_result) -> None:
    del tokens
    del dfs_result
    torch.cuda.empty_cache()


V2_CONFIG = WorkerConfig(
    model_name="/kaggle/input/notebooks/mirzamilanfarabi/qwen3-4b-grids15-sft139",
    max_seq_length=4096,
    model_load_kwargs=dict(
        dtype=torch.float16,
        attn_implementation="sdpa",
    ),
    peft_params=COMMON_PEFT_PARAMS,
    train_args=TRAIN_ARGS,
    trainer_class=UnslothV2FixedTrainer,
    install_attention=None,
    post_peft_setup=_post_peft_setup_v2,
    post_train_cleanup=_post_train_cleanup_v2,
    build_batches=build_batches_single,
    dir_outputs="/kaggle/tmp/inference_outputs",
    post_batch_cleanup=_post_batch_cleanup_v2,
    disable_amp_grad_scaler=False,
)


def worker(rank: int, queue, end_time: float) -> None:
    worker_core(rank, queue, end_time, V2_CONFIG)