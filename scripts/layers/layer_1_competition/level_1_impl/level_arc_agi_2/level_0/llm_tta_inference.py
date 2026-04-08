"""LLM-TTA config and pure helpers (no level_2 sibling imports; orchestration in level_3.llm_tta_runner)."""

import math
from dataclasses import dataclass
from typing import Any, Mapping

Grid = list[list[int]]


@dataclass(frozen=True)
class LlmTtaDfsConfig:
    """Runtime parameters for llm_tta_dfs strategy."""

    execution_mode: str = "surrogate"  # surrogate|lm_backend
    num_augmentations: int = 8
    beam_width: int = 12
    max_candidates: int = 6
    max_neg_log_score: float = 120.0
    seed: int = 0
    consistency_weight: float = 1.0
    model_weight: float = 1.0
    augmentation_likelihood_weight: float = 1.0
    enable_neural_backend: bool = False  # retained for backward compatibility
    model_path: str | None = None
    lora_path: str | None = None
    max_runtime_sec: float = 0.0
    task_runtime_sec: float = 0.0
    decode_runtime_sec: float = 0.0
    adapt_steps: int = 0
    adapt_batch_size: int = 1
    adapt_gradient_accumulation_steps: int = 1
    adapt_disabled: bool = False
    per_task_adaptation: bool = False
    runtime_attention_mode: str = "auto"  # auto|eager|sdpa
    runtime_disable_compile: bool = False
    runtime_allocator_expandable_segments: bool = True
    runtime_allocator_max_split_size_mb: int = 0
    prefer_cnn_attempt1: bool = False
    candidate_ranker: str = "default"
    turbo_prune_max_nll: float = -math.log(0.2)
    turbo_max_new_tokens: int | None = None
    turbo_inner_loop_wall_sec: float | None = None
    infer_artifact_dir: str | None = None
    infer_artifact_run_name: str = ""


def validate_llm_tta_dfs_config(config: LlmTtaDfsConfig) -> None:
    mode = str(config.execution_mode or "").strip().lower()
    if mode not in ("surrogate", "lm_backend"):
        raise ValueError(f"Invalid llm_tta execution_mode={config.execution_mode!r}. Use surrogate|lm_backend.")
    if mode == "surrogate":
        lm_fields_set = (
            bool(config.model_path)
            or bool(config.lora_path)
            or bool(config.enable_neural_backend)
            or bool(config.per_task_adaptation)
        )
        if lm_fields_set:
            raise ValueError(
                "LM-only options were provided in surrogate mode. "
                "Set execution_mode='lm_backend' to use model_path/lora_path."
            )
    if mode == "lm_backend" and not str(config.model_path or "").strip():
        raise ValueError("execution_mode='lm_backend' requires llm_model_path.")
    if bool(config.per_task_adaptation):
        if mode != "lm_backend":
            raise ValueError("per_task_adaptation requires execution_mode='lm_backend'.")
        if bool(config.adapt_disabled):
            raise ValueError("per_task_adaptation cannot be used with adapt_disabled=True.")
        if int(config.adapt_steps or 0) < 1:
            raise ValueError("per_task_adaptation requires adapt_steps >= 1.")
    cr = str(config.candidate_ranker or "default").strip().lower()
    if cr not in ("default", "kgmon", "probmul"):
        raise ValueError(f"Invalid candidate_ranker={config.candidate_ranker!r}. Use default|kgmon|probmul.")


def llm_tta_grid_hw(grid: Grid) -> tuple[int, int]:
    if not grid:
        return 0, 0
    return len(grid), len(grid[0])


def empty_arc_grid_like(grid: Grid) -> Grid:
    return [[0 for _ in row] for row in grid]


def coerce_arc_grid(grid: Any, fallback: Grid) -> Grid:
    if not isinstance(grid, list):
        return fallback
    if not grid:
        return []
    if not all(isinstance(row, list) for row in grid):
        return fallback
    width = len(grid[0])
    if any(len(row) != width for row in grid):
        return fallback
    try:
        return [[int(v) % 10 for v in row] for row in grid]
    except Exception:
        return fallback


def collect_llm_tta_support_grids(task_payload: Mapping[str, Any] | None, default_grid: Grid) -> list[Grid]:
    support: list[Grid] = []
    if not task_payload:
        return [default_grid]
    train = task_payload.get("train")
    if isinstance(train, list):
        for pair in train:
            if not isinstance(pair, dict):
                continue
            out_grid = pair.get("output")
            if isinstance(out_grid, list):
                support.append(coerce_arc_grid(out_grid, default_grid))
    if support:
        return support
    support.append(default_grid)
    return support


def build_cell_probs_from_support_grids(grids: list[Grid], h: int, w: int) -> list[list[list[float]]]:
    probs = [[[0.0 for _ in range(10)] for _ in range(w)] for _ in range(h)]
    if not grids or h <= 0 or w <= 0:
        return probs
    for r in range(h):
        for c in range(w):
            counts = [1e-3 for _ in range(10)]
            for grid in grids:
                if r < len(grid) and c < len(grid[r]):
                    color = int(grid[r][c]) % 10
                    counts[color] += 1.0
            total = float(sum(counts))
            probs[r][c] = [float(v / total) for v in counts]
    return probs


def llm_tta_augment_seed(task_id: str, test_index: int, base_seed: int) -> int:
    return int(base_seed) + sum(ord(ch) for ch in str(task_id)) + int(test_index) * 9973
