"""ARC-AGI-2 contest configuration."""

from typing import Any

from layers.layer_1_competition.level_0_infra.level_0 import ContestConfig


class ARC26Config(ContestConfig):
    """ARC uses grid-structured outputs, not fixed tabular targets."""

    @property
    def target_weights(self) -> dict[str, float]:
        return {}

    @property
    def target_order(self) -> list[str]:
        return []

    @property
    def primary_targets(self) -> list[str]:
        return []

    @property
    def derived_targets(self) -> list[str]:
        return []

    def compute_derived_targets(self, predictions: Any) -> Any:
        return predictions

