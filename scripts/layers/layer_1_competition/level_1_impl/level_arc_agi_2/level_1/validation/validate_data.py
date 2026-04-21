"""ARC JSON contract validation (orchestrator/entrypoint)."""

import json

from pathlib import Path
from typing import Any

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.arc_paths.arc_challenge_filenames import (
    EVAL_CHALLENGE_NAMES,
    TEST_CHALLENGE_NAMES,
    TRAINING_CHALLENGE_NAMES,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.arc_paths.eval_paths import (
    arc_find_first_existing_file,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.validation.validate_challenges import (
    validate_challenges,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.validation.validate_submission_contract import (
    validate_submission_contract,
)

logger = get_logger(__name__)


def _read_json_file(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_challenge_path(root: Path, names: tuple[str, ...]) -> Path:
    found = arc_find_first_existing_file(root, list(names))
    return found if found is not None else root / names[0]


def require_data_root(data_root: str) -> Path:
    """Return ``Path(data_root)`` after asserting the directory exists.

    Small shared helper extracted in Run 6 to dedupe the 3-line
    ``Path(...) + exists() + FileNotFoundError`` idiom repeated across
    ``level_5`` stages (train / tune / submit).
    """
    root = Path(data_root)
    if not root.exists():
        raise FileNotFoundError(f"data_root does not exist: {root}")
    return root


def validate_arc_inputs(data_root: str, max_targets: int = 0) -> None:
    """Validate ARC challenge files and sample submission contract."""
    root = require_data_root(data_root)

    train_challenges = _resolve_challenge_path(root, TRAINING_CHALLENGE_NAMES)
    eval_challenges = _resolve_challenge_path(root, EVAL_CHALLENGE_NAMES)
    test_challenges = _resolve_challenge_path(root, TEST_CHALLENGE_NAMES)
    sample_submission = root / "sample_submission.json"

    for p in [train_challenges, eval_challenges, test_challenges]:
        if not p.exists():
            raise FileNotFoundError(f"Missing required ARC file: {p}")

    train_data = _read_json_file(train_challenges)
    eval_data = _read_json_file(eval_challenges)
    test_data = _read_json_file(test_challenges)

    validate_challenges(train_data, max_targets=max_targets)
    validate_challenges(eval_data, max_targets=max_targets)
    validate_challenges(test_data, max_targets=max_targets)

    if sample_submission.exists():
        sample_data = _read_json_file(sample_submission)
        validate_submission_contract(test_data, sample_data)

    logger.info("ARC inputs validated")
    logger.info("  train tasks: %d", len(train_data))
    logger.info("  evaluation tasks: %d", len(eval_data))
    logger.info("  test tasks: %d", len(test_data))
