"""Multi-GPU worker factory for ARC local/Kaggle runners."""

import os
import time

from layers.layer_0_core.level_0 import get_torch

torch = get_torch()


def make_local_worker(worker_fn):
    def local_worker(rank, queue, end_time):
        os.environ["CUDA_VISIBLE_DEVICES"] = str(rank)

        torch.set_default_device("cpu")

        # Fix Unsloth patching issue
        if rank > 0:
            while not os.path.exists(f"/kaggle/worker{rank-1}"):
                time.sleep(5)

        with open(f"/kaggle/worker{rank}", "w") as f:
            f.write("Ok")

        print(f"[Rank {rank}] start!")

        worker_fn(rank, queue, end_time)

        print(f"[Rank {rank}] done!")

    return local_worker
