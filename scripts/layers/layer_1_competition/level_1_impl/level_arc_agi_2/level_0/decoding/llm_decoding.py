"""ARC-facing names and docs for NVARC ``turbo_dfs`` (implementation in competition infra)."""

from layers.layer_1_competition.level_0_infra.level_3.lm_backend.turbo_dfs import (
    DEFAULT_TURBO_DFS_ALLOWED_TOKEN_IDS,
    NVARC_QWEN_GRID_SOLVER_TOKEN_VOCAB,
    TURBO_DFS_DEFAULT_EOS_ID,
    TURBO_DFS_DEFAULT_INNER_LOOP_WALL_SEC,
    TURBO_DFS_DEFAULT_PAD_ID,
    TurboSuffixes,
    inference_turbo_dfs,
    turbo_dfs,
)

# Single source of truth for preset vocab ids is infra ``NVARC_QWEN_GRID_SOLVER_TOKEN_VOCAB``.
REFERENCE_ARC_VOCAB: dict[str, int] = NVARC_QWEN_GRID_SOLVER_TOKEN_VOCAB
REFERENCE_ARC_TOKENS: tuple[int, ...] = DEFAULT_TURBO_DFS_ALLOWED_TOKEN_IDS
REFERENCE_USER_TOKEN_ID: int = 11
REFERENCE_ASSISTANT_TOKEN_ID: int = 12
REFERENCE_PAD_ID: int = TURBO_DFS_DEFAULT_PAD_ID
REFERENCE_EOS_ID: int = TURBO_DFS_DEFAULT_EOS_ID
REFERENCE_INNER_LOOP_WALL_SEC: float = TURBO_DFS_DEFAULT_INNER_LOOP_WALL_SEC

__all__ = [
    "REFERENCE_ARC_TOKENS",
    "REFERENCE_ARC_VOCAB",
    "REFERENCE_ASSISTANT_TOKEN_ID",
    "REFERENCE_EOS_ID",
    "REFERENCE_INNER_LOOP_WALL_SEC",
    "REFERENCE_PAD_ID",
    "REFERENCE_USER_TOKEN_ID",
    "TurboSuffixes",
    "inference_turbo_dfs",
    "turbo_dfs",
]
