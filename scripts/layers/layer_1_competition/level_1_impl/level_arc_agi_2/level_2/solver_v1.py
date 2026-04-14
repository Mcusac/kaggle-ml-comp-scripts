"""
Solver v1 — entry point.
"""

from layers.layer_0_core.level_0 import get_torch

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    install_repeat_interleave_attention,
    UnslothFixedTrainer,
    infer_notebook_style_decode_batches,
    COMMON_PEFT_PARAMS, 
    COMMON_TRAIN_ARGS
)

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    WorkerConfig,
    worker_core,
)

torch = get_torch()


TRAIN_ARGS = dict(
    **COMMON_TRAIN_ARGS,
    optim="adamw_8bit",
    fp16=False,
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
    peft_params=COMMON_PEFT_PARAMS,
    train_args=TRAIN_ARGS,
    trainer_class=UnslothFixedTrainer,
    install_attention=install_repeat_interleave_attention,
    post_peft_setup=_post_peft_setup_v1,
    build_batches=infer_notebook_style_decode_batches,
    dir_outputs="/kaggle/inference_outputs",
    disable_amp_grad_scaler=True,
)


def worker(rank: int, queue, end_time: float) -> None:
    worker_core(rank, queue, end_time, V1_CONFIG)