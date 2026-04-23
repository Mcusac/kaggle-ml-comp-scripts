"""Auto-generated package exports."""


from .augmentations import (
    AugmentationSpec,
    Grid,
    IDENTITY_AUGMENTATION,
    apply_augmentation,
    generate_augmentation_specs,
    invert_augmentation,
    invert_color_permutation,
)

from .heuristics import (
    DEFAULT_SUBMIT_HEURISTIC,
    HEURISTIC_QUICK_ORDER,
    HEURISTIC_THOROUGH_ORDER,
    heuristic_order_for_train_mode,
    predict_attempts_for_heuristic,
    predict_attempts_from_chosen_params,
)

from .stack_policy import (
    stack_explain_stacking_requirements,
    stack_raise_if_unsupported_strategy,
)

from .submit_limits import read_submit_max_tasks_env

from .tuning_io import load_chosen_params_from_tuned_config

__all__ = [
    "AugmentationSpec",
    "DEFAULT_SUBMIT_HEURISTIC",
    "Grid",
    "HEURISTIC_QUICK_ORDER",
    "HEURISTIC_THOROUGH_ORDER",
    "IDENTITY_AUGMENTATION",
    "apply_augmentation",
    "generate_augmentation_specs",
    "heuristic_order_for_train_mode",
    "invert_augmentation",
    "invert_color_permutation",
    "load_chosen_params_from_tuned_config",
    "predict_attempts_for_heuristic",
    "predict_attempts_from_chosen_params",
    "read_submit_max_tasks_env",
    "stack_explain_stacking_requirements",
    "stack_raise_if_unsupported_strategy",
]
