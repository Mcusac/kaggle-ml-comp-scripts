"""Qwen3 attention monkey-patches for Unsloth (GQA expansion variants)."""

from torch.nn.functional import scaled_dot_product_attention

from layers.layer_0_core.level_0 import get_torch

_torch = get_torch()


def _repeat_interleave_attention(Q, K, V, *args, **kwargs):
    """Manual SDPA with GQA expansion via ``repeat_interleave``."""
    Q = Q.transpose(1, 2)
    K = K.transpose(1, 2)
    V = V.transpose(1, 2)

    num_q_heads = Q.shape[1]
    num_kv_heads = K.shape[1]
    if num_q_heads != num_kv_heads:
        factor = num_q_heads // num_kv_heads
        K = K.repeat_interleave(factor, dim=1)
        V = V.repeat_interleave(factor, dim=1)

    scale = Q.shape[-1] ** -0.5
    scores = _torch.matmul(Q, K.transpose(-2, -1)) * scale
    weights = _torch.softmax(scores.float(), dim=-1).to(Q.dtype)
    out = _torch.matmul(weights, V)
    return out.transpose(1, 2)


def install_repeat_interleave_attention() -> None:
    import unsloth.models.qwen3 as qwen3_module

    qwen3_module.flash_attn_func = _repeat_interleave_attention


def _sdpa_expand_attention(q, k, v, mask=None, is_causal=False, **kwargs):
    """SDPA + ``expand`` for memory-efficient GQA."""
    q = q.transpose(1, 2)
    k = k.transpose(1, 2)
    v = v.transpose(1, 2)

    n_heads = q.shape[1]
    n_kv_heads = k.shape[1]

    if n_heads != n_kv_heads:
        n_groups = n_heads // n_kv_heads
        bsz, _, seq_len, head_dim = k.shape
        k = k[:, :, None, :, :].expand(-1, -1, n_groups, -1, -1).reshape(bsz, n_heads, seq_len, head_dim)
        v = v[:, :, None, :, :].expand(-1, -1, n_groups, -1, -1).reshape(bsz, n_heads, seq_len, head_dim)

    out = scaled_dot_product_attention(q, k, v, attn_mask=mask, is_causal=False)
    return out.transpose(1, 2)


def install_sdpa_attention() -> None:
    import unsloth.models.qwen3 as qwen3_module

    qwen3_module.flash_attn_func = _sdpa_expand_attention