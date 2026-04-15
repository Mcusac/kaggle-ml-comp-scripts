"""
Multi-task / multi-head training configuration extensions.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional

from layers.layer_0_core.level_1 import TrainingConfig


@dataclass
class MultiTaskTrainingConfig(TrainingConfig):
    """
    Training config with per-task override support.

    Allows task-specific hyperparameter overrides without
    encoding domain semantics.
    """

    # task_id -> override params
    # Example:
    # {
    #   "task_a": {"learning_rate": 1e-3},
    #   "task_b": {"batch_size": 64},
    # }
    per_task_hyperparams: Optional[
        Dict[str, Dict[str, Any]]
    ] = None


    def get_task_params(self, task_id: str) -> Dict[str, Any]:
        """
        Get effective hyperparameters for a task.

        Base params + overrides.
        """
        base = self.to_dict()

        overrides = {}

        if self.per_task_hyperparams:
            overrides = self.per_task_hyperparams.get(task_id, {})

        base.update(overrides)

        return base