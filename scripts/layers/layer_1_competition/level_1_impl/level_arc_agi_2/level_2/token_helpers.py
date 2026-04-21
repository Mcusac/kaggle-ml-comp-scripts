"""Tokenizer / dtype / adapter helpers shared by the ARC LM backends (re-exports + Qwen helpers)."""

from typing import Any

from layers.layer_1_competition.level_0_infra.level_0 import (
    load_adapter_state_dict,
    resolve_digit_token_ids,
    resolve_newline_token_id,
    resolve_turbo_token_table,
    torch_dtype_from_config,
    unsloth_available,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    ArcQwenGridChatFormatter,
)


def resolve_arc_digit_token_ids(tokenizer: Any) -> list[int]:
    """Resolve token ids for digit strings '0'..'9' (must be single-token each)."""
    return resolve_digit_token_ids(tokenizer)


def resolve_turbo_arc_token_table(
    tokenizer: Any,
    formatter: ArcQwenGridChatFormatter,
) -> tuple[tuple[int, ...], int, int]:
    """Return ``(arc_tokens, pad_id, eos_id)`` for NVARC-style ``turbo_dfs`` branching."""
    return resolve_turbo_token_table(tokenizer, str(formatter.im_end))