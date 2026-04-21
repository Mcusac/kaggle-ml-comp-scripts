"""Contest-agnostic local runner helpers."""

from .local_multi_gpu_worker import make_local_worker

__all__ = ["make_local_worker"]
