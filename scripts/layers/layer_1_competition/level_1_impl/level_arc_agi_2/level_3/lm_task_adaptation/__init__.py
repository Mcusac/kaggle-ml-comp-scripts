"""Per-task Unsloth LoRA adaptation subpackage.

Public surface: ``run_unsloth_task_adaptation`` + ``build_task_training_rows``.
Internal modules: ``training_rows`` (data prep), ``runner`` (trainer execution).
"""

from .runner import run_unsloth_task_adaptation
from .training_rows import build_task_training_rows

__all__ = ["run_unsloth_task_adaptation", "build_task_training_rows"]
