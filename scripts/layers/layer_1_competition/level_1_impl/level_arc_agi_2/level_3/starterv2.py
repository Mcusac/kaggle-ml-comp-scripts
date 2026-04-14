import os

os.environ["TORCH_COMPILE_DISABLE"] = "1"
os.environ["UNSLOTH_USE_COMPILED"] = "0"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = (
    "expandable_segments:True,max_split_size_mb:64"
)

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import run_entry
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2 import worker_v2


run_entry(
    worker_fn=worker_v2,
    nprocs=2,
)