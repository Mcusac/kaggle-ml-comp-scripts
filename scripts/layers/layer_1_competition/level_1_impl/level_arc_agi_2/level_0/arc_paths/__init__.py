"""Auto-generated package exports."""


from .arc_challenge_filenames import (
    EVAL_CHALLENGE_NAMES,
    EVAL_SOLUTION_NAMES,
    TEST_CHALLENGE_NAMES,
    TRAINING_CHALLENGE_NAMES,
    TRAINING_SOLUTION_NAMES,
)

from .eval_paths import arc_find_first_existing_file

from .kaggle_arc_challenge_paths import (
    arc_kaggle_challenges_json_path,
    arc_kaggle_default_challenge_bundle_root,
    arc_kaggle_evaluation_solutions_json_path,
)

__all__ = [
    "EVAL_CHALLENGE_NAMES",
    "EVAL_SOLUTION_NAMES",
    "TEST_CHALLENGE_NAMES",
    "TRAINING_CHALLENGE_NAMES",
    "TRAINING_SOLUTION_NAMES",
    "arc_find_first_existing_file",
    "arc_kaggle_challenges_json_path",
    "arc_kaggle_default_challenge_bundle_root",
    "arc_kaggle_evaluation_solutions_json_path",
]
