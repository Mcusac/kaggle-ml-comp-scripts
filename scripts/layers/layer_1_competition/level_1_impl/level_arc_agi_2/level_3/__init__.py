"""Auto-generated mixed exports."""


from . import (
    lm_task_adaptation,
    neural_eval_score,
    trainer_registry,
)

from .lm_task_adaptation import *
from .neural_eval_score import *
from .trainer_registry import *

from .extend_subparsers import extend_subparsers

from .postprocess_handlers import (
    benchmark_rankers_cmd,
    score_submission_cmd,
)

__all__ = (
    list(lm_task_adaptation.__all__)
    + list(neural_eval_score.__all__)
    + list(trainer_registry.__all__)
    + [
        "benchmark_rankers_cmd",
        "extend_subparsers",
        "score_submission_cmd",
    ]
)
