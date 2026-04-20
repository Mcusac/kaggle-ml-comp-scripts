"""Qwen3 attention patch: SDPA + expand GQA (v3).

Memory-efficient GQA using ``torch.nn.functional.scaled_dot_product_attention``
plus zero-copy ``expand`` for K/V so group expansion consumes no extra VRAM.
"""

from torch.nn.functional import scaled_dot_product_attention


def _sdpa_expand_attention(q, k, v, mask=None, is_causal=False, **kwargs):
    """
    Memory-efficient GQA attention using torch.nn.functional.scaled_dot_product_attention.
    Uses ``expand`` instead of ``repeat_interleave`` so K/V copies share memory.
    Input shape: (bsz, seqlen, num_heads, head_dim).
    """
    q = q.transpose(1, 2)
    k = k.transpose(1, 2)
    v = v.transpose(1, 2)

    n_heads = q.shape[1]
    n_kv_heads = k.shape[1]

    if n_heads != n_kv_heads:
        n_groups = n_heads // n_kv_heads
        bsz, _, seq_len, head_dim = k.shape
        # expand is a zero-copy view — uses no extra VRAM
        k = k[:, :, None, :, :].expand(-1, -1, n_groups, -1, -1).reshape(bsz, n_heads, seq_len, head_dim)
        v = v[:, :, None, :, :].expand(-1, -1, n_groups, -1, -1).reshape(bsz, n_heads, seq_len, head_dim)

    out = scaled_dot_product_attention(q, k, v, attn_mask=mask, is_causal=False)
    return out.transpose(1, 2)


def install_sdpa_attention() -> None:
    """Monkey-patch Qwen3 to use the SDPA + expand GQA attention (v3)."""
    import unsloth.models.qwen3 as qwen3_module

    qwen3_module.flash_attn_func = _sdpa_expand_attention
