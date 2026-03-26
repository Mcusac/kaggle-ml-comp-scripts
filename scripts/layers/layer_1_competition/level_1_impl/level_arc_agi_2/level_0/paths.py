"""ARC-AGI-2 path definitions."""

from pathlib import Path
from typing import Optional

from layers.layer_1_competition.level_0_infra.level_0 import ContestPaths


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
        return self._find_existing(
            [
                "arc-agi_training_challenges.json",
                "arc-agi_training-challenges.json",
            ]
        )

    def training_solutions_path(self) -> Path:
        return self._find_existing(
            [
                "arc-agi_training_solutions.json",
                "arc-agi_training-solutions.json",
            ]
        )

    def evaluation_challenges_path(self) -> Path:
        return self._find_existing(
            [
                "arc-agi_evaluation_challenges.json",
                "arc-agi_evaluation-challenges.json",
            ]
        )

    def evaluation_solutions_path(self) -> Path:
        return self._find_existing(
            [
                "arc-agi_evaluation_solutions.json",
                "arc-agi_evaluation-solutions.json",
            ]
        )

    def test_challenges_path(self) -> Path:
        return self._find_existing(
            [
                "arc-agi_test_challenges.json",
                "arc-agi_test-challenges.json",
            ]
        )

    def sample_submission_path(self) -> Path:
        return self.get_data_root() / "sample_submission.json"

    def submission_output_path(self) -> Path:
        return self.get_output_dir() / "submission.json"

