"""
Centralized torch import handling.
Uses lru_cache for testability (cache_clear between tests).
"""

import functools
from typing import Any


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


class TorchAbsentModule:
    """Stand-in base when PyTorch is not installed.

    Vision ABCs combine this with :class:`abc.ABC`. Using :class:`object` as the
    non-torch base breaks MRO; this type provides a minimal cooperative
    :meth:`__init__` for :func:`super` chains. Training/inference still require
    a real ``torch`` install.
    """

    def __init__(self) -> None:
        pass


def get_nn_module_base_class():
    """Return ``torch.nn.Module`` if PyTorch is available, else :class:`TorchAbsentModule`."""
    t = get_torch()
    return t.nn.Module if t is not None else TorchAbsentModule


def get_vision_module_and_tensor_types() -> tuple[Any, Any]:
    """Return ``(nn.Module, Tensor)`` for annotations when torch exists, else ``(Any, Any)``."""
    t = get_torch()
    if t is not None:
        return t.nn.Module, t.Tensor
    return Any, Any
