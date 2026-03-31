"""Reusable pipeline shells (infra-level).

These are structural shells only: validate -> stage1 -> stage2, etc.
Contest-specific policy stays in contest packages.
"""

from .validate_train_submit import ValidateTrainSubmitPipelineResultShell

__all__ = [
    "ValidateTrainSubmitPipelineResultShell",
]

