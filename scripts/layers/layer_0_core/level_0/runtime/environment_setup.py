"""Lightweight process environment hooks for CLI entry points."""

from typing import Optional


def setup_environment(
    model_name: Optional[str] = None,
    download_weights: bool = True,
) -> None:
    """
    Best-effort runtime environment for training/inference.

    Reserved for cache dirs, HF/torch paths, etc. Safe no-op until extended.
    """
    _ = (model_name, download_weights)
