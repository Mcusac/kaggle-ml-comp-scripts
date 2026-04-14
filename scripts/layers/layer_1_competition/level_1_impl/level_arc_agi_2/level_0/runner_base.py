import os
import time
import json
import argparse
import torch.multiprocessing as mp

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


def run_entry(worker_fn, nprocs=2, test_filter=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--end-time", type=float, default=0.0)
    args = parser.parse_args()

    rerun_mode = os.getenv("KAGGLE_IS_COMPETITION_RERUN")

    if rerun_mode:
        test_path = "/kaggle/input/competitions/arc-prize-2026-arc-agi-2/arc-agi_test_challenges.json"
    else:
        test_path = "/kaggle/input/competitions/arc-prize-2026-arc-agi-2/arc-agi_evaluation_challenges.json"

    with open(test_path, "r") as f:
        data = json.load(f)

    queue = mp.Manager().Queue()

    for key in sorted(data.keys()):
        if not rerun_mode and test_filter is not None:
            if key not in test_filter:
                continue
        queue.put(key)

    for _ in range(nprocs):
        queue.put(None)

    mp.spawn(
        make_local_worker(worker_fn),
        args=(queue, args.end_time),
        nprocs=nprocs,
    )