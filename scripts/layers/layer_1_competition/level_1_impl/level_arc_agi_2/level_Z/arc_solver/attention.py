"""
Attention patchers for Qwen3.

Two implementations are provided:
  - patch_repeat_interleave_attention: used by v1/v2 — simple GQA via repeat_interleave.
  - patch_sdpa_attention:             used by v3  — memory-efficient GQA via expand + SDPA.

Call the appropriate ``install_*`` function at process startup before loading the model.
"""

import unsloth.models.qwen3 as qwen3_module

from layers.layer_0_core.level_0 import get_torch
from torch.nn.functional import scaled_dot_product_attention

torch = get_torch()


# ---------------------------------------------------------------------------
# v1 / v2  — repeat_interleave GQA  (simple, slightly higher VRAM)
# ---------------------------------------------------------------------------

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
    qwen3_module.flash_attn_func = _repeat_interleave_attention


# ---------------------------------------------------------------------------
# v3 — SDPA + expand GQA  (zero-copy expansion, lower VRAM)
# ---------------------------------------------------------------------------

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
    qwen3_module.flash_attn_func = _sdpa_expand_attention