"""Per-task LM adaptation orchestration (infra; contest injects factories)."""

from .session import prepare_llm_tta_backend, restore_adapter_safely

__all__ = [
    "prepare_llm_tta_backend",
    "restore_adapter_safely",
]
