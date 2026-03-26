"""
Centralized torch import handling.
Uses lru_cache for testability (cache_clear between tests).
"""

import functools


@functools.lru_cache(maxsize=1)
def _load_torch():
    """Load torch module. Cached; call cache_clear() to reset."""
    try:
        import torch
        return torch
    except ImportError:
        return None


def get_torch():
    """Get torch module or None if unavailable. Cached."""
    return _load_torch()


def is_torch_available() -> bool:
    """Check if torch is available."""
    return get_torch() is not None
