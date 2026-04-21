"""Composite argparse wiring for full LLM TTA flag surface."""

from typing import Any

from .adaptation import add_llm_tta_adaptation
from .augmentation import add_llm_tta_augmentation
from .core import add_llm_tta_core
from .decoding import add_llm_tta_decoding
from .inference import add_llm_tta_inference
from .inference_artifacts import add_llm_tta_artifacts
from .runtime import add_llm_tta_runtime


def add_llm_tta_args(parser: Any) -> None:
    add_llm_tta_core(parser)
    add_llm_tta_adaptation(parser)
    add_llm_tta_augmentation(parser)
    add_llm_tta_decoding(parser)
    add_llm_tta_inference(parser)
    add_llm_tta_artifacts(parser)
    add_llm_tta_runtime(parser)


__all__ = ["add_llm_tta_args"]
