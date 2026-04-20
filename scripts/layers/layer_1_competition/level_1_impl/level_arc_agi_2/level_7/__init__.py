"""Orchestration for ARC AGI 2 competition (thin re-export of ``handlers``)."""

from .handlers import (
    FRAMEWORK_SUBPARSER_NAMES_TO_SKIP,
    arc_llm_kwargs_from_args,
    benchmark_rankers_cmd,
    extend_subparsers,
    get_handlers,
    score_submission_cmd,
    submit,
    train,
    train_and_submit,
    tune,
    tune_and_submit,
    validate_data,
)

__all__ = [
    "FRAMEWORK_SUBPARSER_NAMES_TO_SKIP",
    "arc_llm_kwargs_from_args",
    "benchmark_rankers_cmd",
    "extend_subparsers",
    "get_handlers",
    "score_submission_cmd",
    "submit",
    "train",
    "train_and_submit",
    "tune",
    "tune_and_submit",
    "validate_data",
]
