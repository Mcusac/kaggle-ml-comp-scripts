"""Canonical ARC challenge / solution JSON filename fallbacks.

ARC datasets ship filenames with either underscore or hyphen between the split
name and the suffix (``training_challenges`` vs ``training-challenges``). These
tuples encode the lookup order (preferred first) used across level_0.
"""

TRAINING_CHALLENGE_NAMES: tuple[str, ...] = (
    "arc-agi_training_challenges.json",
    "arc-agi_training-challenges.json",
)

TRAINING_SOLUTION_NAMES: tuple[str, ...] = (
    "arc-agi_training_solutions.json",
    "arc-agi_training-solutions.json",
)

EVAL_CHALLENGE_NAMES: tuple[str, ...] = (
    "arc-agi_evaluation_challenges.json",
    "arc-agi_evaluation-challenges.json",
)

EVAL_SOLUTION_NAMES: tuple[str, ...] = (
    "arc-agi_evaluation_solutions.json",
    "arc-agi_evaluation-solutions.json",
)

TEST_CHALLENGE_NAMES: tuple[str, ...] = (
    "arc-agi_test_challenges.json",
    "arc-agi_test-challenges.json",
)
