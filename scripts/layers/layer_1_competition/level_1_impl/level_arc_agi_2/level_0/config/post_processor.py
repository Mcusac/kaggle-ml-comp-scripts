"""ARC submission post-processing helpers."""

import numpy as np

from copy import deepcopy
from typing import Any

from layers.layer_1_competition.level_0_infra.level_0 import ContestPostProcessor


class ARC26PostProcessor(ContestPostProcessor):
    """Ensure deterministic submission dictionary layout."""

    def apply(self, predictions: np.ndarray) -> np.ndarray:
        return predictions

    def normalize_submission(self, submission: dict[str, list[dict[str, Any]]]) -> dict[str, list[dict[str, Any]]]:
        normalized: dict[str, list[dict[str, Any]]] = {}
        for task_id in sorted(submission.keys()):
            attempts = submission[task_id]
            normalized[task_id] = [deepcopy(item) for item in attempts]
        return normalized

