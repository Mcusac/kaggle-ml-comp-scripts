"""Tokenizer ID resolution for causal LMs (digits, newline, assistant end, pad)."""

from typing import Any

from .nll_scoring import resolve_pad_id


def token_id_for_single_text(tokenizer: Any, text: str) -> int:
    """Return a single token id for ``text`` or raise if it encodes to multiple ids."""
    ids = tokenizer.encode(text, add_special_tokens=False)
    if not isinstance(ids, list) or len(ids) != 1:
        raise ValueError(f"Expected {text!r} to encode to 1 token, got {ids!r}")
    return int(ids[0])


def resolve_digit_token_ids(tokenizer: Any) -> list[int]:
    """Resolve token ids for digit strings ``'0'``..``'9'`` (must be single-token each)."""
    return [token_id_for_single_text(tokenizer, str(i)) for i in range(10)]


def resolve_newline_token_id(tokenizer: Any) -> int:
    """Resolve token id for newline (must be single-token)."""
    return token_id_for_single_text(tokenizer, "\n")


def resolve_turbo_eos_id(tokenizer: Any, im_end: str) -> int:
    """Single token id for assistant segment end (e.g. chat template ``im_end``)."""
    ids = tokenizer.encode(str(im_end), add_special_tokens=False)
    if not isinstance(ids, list) or len(ids) != 1:
        raise ValueError(
            f"im_end {im_end!r} must encode to exactly one token for turbo_dfs; got {ids!r}"
        )
    return int(ids[0])


def resolve_turbo_token_table(
    tokenizer: Any,
    im_end: str,
) -> tuple[tuple[int, ...], int, int]:
    """Return ``(branch_token_ids, pad_id, eos_id)`` for NVARC-style ``turbo_dfs`` branching."""
    digit_ids = tuple(token_id_for_single_text(tokenizer, str(i)) for i in range(10))
    newline_id = resolve_newline_token_id(tokenizer)
    eos_id = resolve_turbo_eos_id(tokenizer, im_end)
    branch_tokens = digit_ids + (newline_id, eos_id)
    pad_id = resolve_pad_id(tokenizer, None)
    return branch_tokens, pad_id, eos_id