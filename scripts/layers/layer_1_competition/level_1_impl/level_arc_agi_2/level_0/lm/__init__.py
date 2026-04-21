"""Auto-generated package exports."""


from .lm_attention_patcher_repeat_interleave import (
    install_repeat_interleave_attention,
    torch,
)

from .lm_attention_patcher_sdpa import install_sdpa_attention

__all__ = [
    "install_repeat_interleave_attention",
    "install_sdpa_attention",
    "torch",
]
