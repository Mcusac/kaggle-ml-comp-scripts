"""Handler dispatch registry."""

from typing import Callable

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3 import (
    benchmark_rankers_cmd,
    score_submission_cmd,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_8 import (
    submit,
    train,
    train_and_submit,
    tune,
    tune_and_submit,
    validate_data,
)



def get_handlers() -> dict[str, Callable]:
    return {
        "validate_data": validate_data,
        "train": train,
        "tune": tune,
        "submit": submit,
        "score_submission": score_submission_cmd,
        "benchmark_rankers": benchmark_rankers_cmd,
        "train_and_submit": train_and_submit,
        "tune_and_submit": tune_and_submit,
    }
