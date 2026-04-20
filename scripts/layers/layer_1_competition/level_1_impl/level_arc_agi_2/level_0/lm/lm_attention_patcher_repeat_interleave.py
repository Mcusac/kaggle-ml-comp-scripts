"""Qwen3 attention patch: repeat_interleave GQA (v1/v2).

Manual scaled-dot-product attention with GQA expansion via ``repeat_interleave``.
Simple path, slightly higher VRAM than the SDPA variant.
"""

from layers.layer_0_core.level_0 import get_torch

torch = get_torch()


def _repeat_interleave_attention(Q, K, V, *args, **kwargs):
    """
    Manual scaled-dot-product attention with GQA expansion via repeat_interleave.
    Input shape: (bsz, seqlen, num_heads, head_dim).
    """
    Q = Q.transpose(1, 2)  # (bsz, num_heads, seqlen, head_dim)
    K = K.transpose(1, 2)
    V = V.transpose(1, 2)

    num_q_heads = Q.shape[1]
    num_kv_heads = K.shape[1]
    if num_q_heads != num_kv_heads:
        factor = num_q_heads // num_kv_heads
        K = K.repeat_interleave(factor, dim=1)
        V = V.repeat_interleave(factor, dim=1)

    scale = Q.shape[-1] ** -0.5
    scores = torch.matmul(Q, K.transpose(-2, -1)) * scale
    weights = torch.softmax(scores.float(), dim=-1).to(Q.dtype)
    out = torch.matmul(weights, V)
    return out.transpose(1, 2)  # (bsz, seqlen, num_heads, head_dim)


def install_repeat_interleave_attention() -> None:
    """Monkey-patch Qwen3 to use the repeat_interleave GQA attention (v1/v2)."""
    import unsloth.models.qwen3 as qwen3_module

    qwen3_module.flash_attn_func = _repeat_interleave_attention
