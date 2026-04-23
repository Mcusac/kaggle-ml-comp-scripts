"""High-level inference artifact layout + writers for LLM-TTA DFS."""

import os

from typing import Any

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_0_infra.level_0.lm import LlmTtaDfsConfig

from .store import (
    infer_ensure_run_layout,
    infer_eval_basekey,
    infer_save_decoded_result_shard,
    infer_save_intermediate_candidates,
    infer_shard_basename,
)

_logger = get_logger(__name__)


def prepare_artifact_layout(
    config: LlmTtaDfsConfig,
    task_id: str,
    test_index: int,
) -> tuple[str | None, str | None, str, dict[str, Any]]:
    """Resolve ``(infer_out, inter_dir, basekey, artifact_meta)`` from config.

    Returns ``(None, None, basekey, {})`` when no artifact root is configured.
    """
    artifact_root = str(getattr(config, "infer_artifact_dir", None) or "").strip()
    basekey = infer_eval_basekey(str(task_id), int(test_index))
    if not artifact_root:
        return None, None, basekey, {}
    infer_out, _, inter_dir = infer_ensure_run_layout(artifact_root)
    artifact_meta: dict[str, Any] = {
        "infer_artifact_dir": artifact_root,
        "inference_outputs_dir": infer_out,
        "intermediate_candidates_dir": inter_dir,
        "infer_artifact_run_name": str(getattr(config, "infer_artifact_run_name", "") or ""),
        "basekey": basekey,
    }
    return infer_out, inter_dir, basekey, artifact_meta


def write_decoded_shard(infer_out: str, basekey: str, aug_index: int, shard: list[dict[str, Any]]) -> None:
    """Write a single augmentation's decoded-result shard; swallow+log on failure."""
    if not (infer_out and shard):
        return
    shard_path = os.path.join(infer_out, infer_shard_basename(basekey, aug_index))
    try:
        infer_save_decoded_result_shard(shard_path, shard)
    except Exception as e:
        _logger.warning("⚠️ inference_outputs shard write failed (%s): %s", shard_path, e)


def write_intermediate_candidates(
    inter_dir: str,
    basekey: str,
    task_id: str,
    test_index: int,
    mode: str,
    config: LlmTtaDfsConfig,
    predictions: list[Any],
) -> None:
    """Write the full per-task candidate JSON; swallow+log on failure."""
    if not inter_dir:
        return
    try:
        infer_save_intermediate_candidates(
            os.path.join(inter_dir, f"{basekey}.json"),
            {
                "task_id": str(task_id),
                "test_index": int(test_index),
                "basekey": basekey,
                "execution_mode": mode,
                "candidate_ranker": str(config.candidate_ranker or "default"),
                "candidates": [
                    {
                        "aug_key": p.aug_key,
                        "model_score": float(p.model_score),
                        "aug_likelihood_score": float(p.aug_likelihood_score),
                        "grid": [list(row) for row in p.grid],
                    }
                    for p in predictions
                ],
            },
        )
    except Exception as e:
        _logger.warning("⚠️ intermediate_candidates write failed: %s", e)