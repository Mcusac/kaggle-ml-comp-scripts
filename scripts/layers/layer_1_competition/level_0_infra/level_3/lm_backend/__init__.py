"""Shared LM backend protocol and reference mock implementation."""

from .mock_backend import MockLmBackend
from .protocol import Grid, LmBackend, LmBackendConfig

__all__ = ["Grid", "LmBackend", "LmBackendConfig", "MockLmBackend"]
