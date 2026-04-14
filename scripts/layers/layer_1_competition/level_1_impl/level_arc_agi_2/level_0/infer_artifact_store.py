"""Load/save bz2-pickled decode shards (reference notebook layout; stdlib only).

On-disk layout under an artifact *root* directory (NVARC / parity map):

- ``{root}/inference_outputs/`` — flat files named ``{basekey}.{aug_label}`` (no ``.bz2``
  suffix in the filename; content is bz2-compressed pickle), same as
  ``pickle.dump(..., bz2.BZ2File(os.path.join(dir_outputs, subkey), "w"))``.
  ``basekey`` must be ``f"{task_id}_{test_index}"`` so :func:`infer_load_decoded_results_from_dir`
  groups agree with ``eval_build_basekey_truth_map``.
- ``{root}/decoded_results/`` — optional materialized :class:`DecodedStore`
  (:func:`infer_finalize_artifact_root`) for offline tooling.
- ``{root}/intermediate_candidates/`` — JSON per basekey with pre-merge candidates
  (:func:`infer_save_intermediate_candidates`).
"""

import bz2
import json
import os
import pickle

from typing import Any

GuessDict = dict[str, Any]
DecodedStore = dict[str, dict[str, GuessDict]]


def infer_eval_basekey(task_id: str, test_index: int) -> str:
    """Label / shard prefix matching ``eval_build_basekey_truth_map``."""
    return f"{task_id}_{int(test_index)}"


def infer_shard_basename(basekey: str, aug_index: int) -> str:
    """Filename (relative to ``inference_outputs``) for one augmentation's beam list."""
    return f"{basekey}.a{int(aug_index)}"


def infer_ensure_run_layout(artifact_root: str) -> tuple[str, str, str]:
    """Create ``inference_outputs``, ``decoded_results``, ``intermediate_candidates`` under root."""
    root = os.path.normpath(str(artifact_root).strip())
    infer_out = os.path.join(root, "inference_outputs")
    decoded = os.path.join(root, "decoded_results")
    inter = os.path.join(root, "intermediate_candidates")
    for d in (infer_out, decoded, inter):
        os.makedirs(d, exist_ok=True)
    return infer_out, decoded, inter


def infer_save_intermediate_candidates(path: str, payload: dict[str, Any]) -> None:
    """Write one UTF-8 JSON file (pre-rank candidate listing)."""
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)


def infer_finalize_artifact_root(artifact_root: str, *, run_name: str = "") -> dict[str, Any]:
    """Load shards from ``inference_outputs``, persist :class:`DecodedStore` + manifest under ``decoded_results``."""
    infer_out, decoded_dir, _ = infer_ensure_run_layout(artifact_root)
    store = infer_load_decoded_results_from_dir(infer_out, run_name=str(run_name or ""))
    pkl_path = os.path.join(decoded_dir, "decoded_store.pkl")
    with open(pkl_path, "wb") as f:
        pickle.dump(store, f, protocol=4)
    manifest = {
        "artifact_root": os.path.normpath(str(artifact_root).strip()),
        "inference_outputs_dir": infer_out,
        "run_name": str(run_name or ""),
        "num_base_keys": len(store),
        "num_flat_guesses": int(sum(len(bucket) for bucket in store.values())),
        "base_keys": sorted(store.keys()),
    }
    man_path = os.path.join(decoded_dir, "manifest.json")
    with open(man_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    return {"decoded_store_pkl": pkl_path, "manifest_json": man_path}


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
