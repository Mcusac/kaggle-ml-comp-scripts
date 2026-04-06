"""ARC-AGI-2 level_0 primitives."""

from .config import ARC26Config
from .data_schema import ARC26DataSchema
from .paths import ARC26Paths
from .post_processor import ARC26PostProcessor
from .dataset import (
    ArcSameShapeGridDataset,
    CANVAS_SIZE,
    NUM_CHANNELS,
    collect_same_shape_train_pairs,
    grid_to_one_hot_tensor,
    logits_to_grid,
)
from .heuristics import (
    DEFAULT_SUBMIT_HEURISTIC,
    HEURISTIC_QUICK_ORDER,
    HEURISTIC_THOROUGH_ORDER,
    heuristic_order_for_train_mode,
    predict_attempts_for_heuristic,
    predict_attempts_from_chosen_params,
)
from .submit_limits import (
    read_submit_max_tasks_env,
)
from .notebook_commands import (
    build_submit_command,
    build_train_and_submit_command,
    build_train_command,
    build_tune_and_submit_command,
    build_tune_command,
    build_validate_data_command,
)
from .validate_data import validate_arc_inputs
from .arc_digit_grid_text import (
    MAX_ARC_GRID_DIM,
    arc_grid_to_text_lines,
    arc_is_valid_grid_shape,
    arc_text_lines_to_grid,
)
from .arc_grids_equal import arc_grids_equal
from .arc_eval_paths import arc_find_first_existing_file
from .arc_stack_policy import (
    stack_explain_stacking_requirements,
    stack_raise_if_unsupported_strategy,
)
from .arc_infer_artifact_store import (
    DecodedStore,
    GuessDict,
    infer_load_decoded_results_from_dir,
    infer_save_decoded_result_shard,
)
from .kaggle_arc_challenge_paths import (
    arc_kaggle_challenges_json_path,
    arc_kaggle_default_challenge_bundle_root,
    arc_kaggle_evaluation_solutions_json_path,
)

__all__ = [
    "ARC26Config",
    "ARC26DataSchema",
    "ARC26Paths",
    "ARC26PostProcessor",
    "ArcSameShapeGridDataset",
    "CANVAS_SIZE",
    "NUM_CHANNELS",
    "collect_same_shape_train_pairs",
    "grid_to_one_hot_tensor",
    "logits_to_grid",
    "DEFAULT_SUBMIT_HEURISTIC",
    "HEURISTIC_QUICK_ORDER",
    "HEURISTIC_THOROUGH_ORDER",
    "heuristic_order_for_train_mode",
    "predict_attempts_for_heuristic",
    "predict_attempts_from_chosen_params",
    "read_submit_max_tasks_env",
    "build_validate_data_command",
    "build_train_command",
    "build_train_and_submit_command",
    "build_tune_command",
    "build_tune_and_submit_command",
    "build_submit_command",
    "validate_arc_inputs",
    "MAX_ARC_GRID_DIM",
    "arc_grid_to_text_lines",
    "arc_is_valid_grid_shape",
    "arc_text_lines_to_grid",
    "arc_grids_equal",
    "arc_find_first_existing_file",
    "DecodedStore",
    "GuessDict",
    "infer_load_decoded_results_from_dir",
    "infer_save_decoded_result_shard",
    "stack_explain_stacking_requirements",
    "stack_raise_if_unsupported_strategy",
    "arc_kaggle_challenges_json_path",
    "arc_kaggle_default_challenge_bundle_root",
    "arc_kaggle_evaluation_solutions_json_path",
]
