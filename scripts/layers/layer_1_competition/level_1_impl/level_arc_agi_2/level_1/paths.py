"""ARC-AGI-2 path definitions."""

from pathlib import Path
from typing import Optional

from layers.layer_1_competition.level_0_infra.level_0 import ContestPaths

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    EVAL_CHALLENGE_NAMES,
    EVAL_SOLUTION_NAMES,
    TEST_CHALLENGE_NAMES,
    TRAINING_CHALLENGE_NAMES,
    TRAINING_SOLUTION_NAMES,
)


class ARC26Paths(ContestPaths):
    """Resolve ARC-AGI-2 dataset paths across Kaggle and local mimic layouts."""

    @property
    def kaggle_dataset_name(self) -> str:
        return "arc-prize-2026-arc-agi-2"

    @property
    def kaggle_competition_name(self) -> Optional[str]:
        return "arc-prize-2026-arc-agi-2"

    @property
    def local_data_path(self) -> str:
        return "../arc-prize-2026-arc-agi-2"

    def _find_existing(self, candidates: list[str]) -> Path:
        root = self.get_data_root()
        for name in candidates:
            path = root / name
            if path.exists():
                return path
        return root / candidates[0]

    def training_challenges_path(self) -> Path:
        return self._find_existing(list(TRAINING_CHALLENGE_NAMES))

    def training_solutions_path(self) -> Path:
        return self._find_existing(list(TRAINING_SOLUTION_NAMES))

    def evaluation_challenges_path(self) -> Path:
        return self._find_existing(list(EVAL_CHALLENGE_NAMES))

    def evaluation_solutions_path(self) -> Path:
        return self._find_existing(list(EVAL_SOLUTION_NAMES))

    def test_challenges_path(self) -> Path:
        return self._find_existing(list(TEST_CHALLENGE_NAMES))

    def sample_submission_path(self) -> Path:
        return self.get_data_root() / "sample_submission.json"

    def submission_output_path(self) -> Path:
        return self.get_output_dir() / "submission.json"