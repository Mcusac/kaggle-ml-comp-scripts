"""Load/save bz2-pickled decode shards (reference notebook layout; stdlib only)."""

from __future__ import annotations

import bz2
import os
import pickle
from typing import Any

GuessDict = dict[str, Any]
DecodedStore = dict[str, dict[str, GuessDict]]


def infer_load_decoded_results_from_dir(store: str, run_name: str = "") -> DecodedStore:
    """Mirror notebook ``ArcDecoder.load_decoded_results``: base_key -> subkey -> sample dict."""
    decoded_results: DecodedStore = {}
    if not os.path.isdir(store):
        return decoded_results
    for key in os.listdir(store):
        path = os.path.join(store, key)
        if not os.path.isfile(path):
            continue
        with bz2.BZ2File(path) as f:
            outputs = pickle.load(f)
        base_key = key.split(".")[0]
        bucket = decoded_results.setdefault(base_key, {})
        if not isinstance(outputs, list):
            continue
        for i, sample in enumerate(outputs):
            bucket[f"{key}{run_name}.out{i}"] = sample
    return decoded_results


def infer_save_decoded_result_shard(path: str, samples: list[Any]) -> None:
    """Write one bz2 pickle file containing a list of decode samples."""
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with bz2.BZ2File(path, "w") as f:
        pickle.dump(samples, f)
