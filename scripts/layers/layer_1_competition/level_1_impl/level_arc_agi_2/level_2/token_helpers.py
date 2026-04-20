"""Tokenizer / dtype / adapter helpers shared by the ARC LM backends."""

import importlib
from pathlib import Path
from typing import Any

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import resolve_pad_id
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    ArcQwenGridChatFormatter,
)


logger = get_logger(__name__)


def _token_id_for_single_text(tokenizer: Any, text: str) -> int:
    """Return a single token id for `text` or raise if it encodes to multiple ids."""
    ids = tokenizer.encode(text, add_special_tokens=False)
    if not isinstance(ids, list) or len(ids) != 1:
        raise ValueError(f"Expected {text!r} to encode to 1 token, got {ids!r}")
    return int(ids[0])


def resolve_arc_digit_token_ids(tokenizer: Any) -> list[int]:
    """Resolve token ids for digit strings '0'..'9' (must be single-token each)."""
    return [_token_id_for_single_text(tokenizer, str(i)) for i in range(10)]


def _resolve_newline_token_id(tokenizer: Any) -> int:
    """Resolve token id for newline (must be single-token)."""
    return _token_id_for_single_text(tokenizer, "\n")


def _resolve_turbo_eos_id(tokenizer: Any, formatter: ArcQwenGridChatFormatter) -> int:
    """Single token id for assistant segment end (reference ``EOS_ID`` / ``im_end``)."""
    ids = tokenizer.encode(str(formatter.im_end), add_special_tokens=False)
    if not isinstance(ids, list) or len(ids) != 1:
        raise ValueError(
            f"im_end {formatter.im_end!r} must encode to exactly one token for turbo_dfs; got {ids!r}"
        )
    return int(ids[0])


def resolve_turbo_arc_token_table(
    tokenizer: Any,
    formatter: ArcQwenGridChatFormatter,
) -> tuple[tuple[int, ...], int, int]:
    """Return ``(arc_tokens, pad_id, eos_id)`` for NVARC-style ``turbo_dfs`` branching."""
    digit_ids = tuple(_token_id_for_single_text(tokenizer, str(i)) for i in range(10))
    newline_id = _resolve_newline_token_id(tokenizer)
    eos_id = _resolve_turbo_eos_id(tokenizer, formatter)
    arc_tokens = digit_ids + (newline_id, eos_id)
    pad_id = resolve_pad_id(tokenizer, None)
    return arc_tokens, pad_id, eos_id


def unsloth_available() -> bool:
    try:
        importlib.import_module("unsloth")
        importlib.import_module("peft")
        return True
    except Exception:
        return False


def torch_dtype_from_config(torch: Any, dtype_str: str) -> Any:
    s = str(dtype_str or "auto").strip().lower()
    if s in ("auto",):
        return torch.float16
    if s in ("float16", "fp16", "half"):
        return torch.float16
    if s in ("bfloat16", "bf16"):
        return torch.bfloat16
    if s in ("float32", "fp32"):
        return torch.float32
    logger.warning("Unknown dtype=%r; using float16 for Unsloth load.", dtype_str)
    return torch.float16


def load_adapter_state_dict(path: str, torch: Any) -> dict[str, Any]:
    """Load a PEFT adapter/state dict from a file or directory (HF PEFT layout)."""
    p = Path(path).expanduser()
    if p.is_dir():
        for name in ("adapter_model.safetensors", "adapter_model.bin", "pytorch_model.bin"):
            cand = p / name
            if cand.is_file():
                return load_adapter_state_dict(str(cand), torch)
        raise FileNotFoundError(f"No adapter_model.* weights found under directory: {path}")
    if not p.is_file():
        raise FileNotFoundError(f"LoRA path is not a file or directory: {path}")
    suf = p.suffix.lower()
    if suf == ".safetensors":
        st = importlib.import_module("safetensors.torch")
        load_file = getattr(st, "load_file")
        return dict(load_file(str(p)))
    try:
        return torch.load(str(p), map_location="cpu", weights_only=True)
    except TypeError:
        return torch.load(str(p), map_location="cpu")
