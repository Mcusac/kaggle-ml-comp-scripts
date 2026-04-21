"""Argparse block builders for LLM-TTA DFS parameters."""

from typing import Any

from .adaptation import add_llm_tta_adaptation
from .augmentation import add_llm_tta_augmentation
from .core import add_llm_tta_core
from .decoding import add_llm_tta_decoding
from .inference import add_llm_tta_inference
from .inference_artifacts import add_llm_tta_artifacts
from .runtime import add_llm_tta_runtime


def add_llm_tta_args(parser: Any) -> None:
    """Register all LLM-TTA DFS flags on ``parser`` (stable subgroup ordering)."""
    add_llm_tta_core(parser)
    add_llm_tta_augmentation(parser)
    add_llm_tta_decoding(parser)
    add_llm_tta_adaptation(parser)
    add_llm_tta_inference(parser)
    add_llm_tta_runtime(parser)
    add_llm_tta_artifacts(parser)


__all__ = [
    "add_llm_tta_adaptation",
    "add_llm_tta_args",
    "add_llm_tta_artifacts",
    "add_llm_tta_augmentation",
    "add_llm_tta_core",
    "add_llm_tta_decoding",
    "add_llm_tta_inference",
    "add_llm_tta_runtime",
]
