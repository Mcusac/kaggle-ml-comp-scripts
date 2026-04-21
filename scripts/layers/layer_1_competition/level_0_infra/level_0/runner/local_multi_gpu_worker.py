"""Multi-GPU worker factory for local/Kaggle-style process pools."""

import os
import time

from layers.layer_0_core.level_0 import get_torch

torch = get_torch()


def make_local_worker(worker_fn, *, worker_sentinel_prefix: str = "/kaggle/worker"):
    """Return a ``local_worker(rank, queue, end_time)`` closure for multi-GPU runs.

    ``worker_sentinel_prefix`` defaults to Kaggle's ``/kaggle/worker`` stem; rank
    ``n`` touches ``{prefix}{n}`` so higher ranks wait on lower ranks.
    """

    def local_worker(rank, queue, end_time):
        os.environ["CUDA_VISIBLE_DEVICES"] = str(rank)

        torch.set_default_device("cpu")

        if rank > 0:
            while not os.path.exists(f"{worker_sentinel_prefix}{rank - 1}"):
                time.sleep(5)

        with open(f"{worker_sentinel_prefix}{rank}", "w") as f:
            f.write("Ok")

        print(f"[Rank {rank}] start!")

        worker_fn(rank, queue, end_time)

        print(f"[Rank {rank}] done!")

    return local_worker