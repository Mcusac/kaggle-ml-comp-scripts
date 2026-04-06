"""Named weight tuples for ``rank_candidate_grids``-style scoring."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TuneLlmTtaWeightPreset:
    """Weights mirroring ``LlmTtaDfsConfig`` ranking terms."""

    name: str
    consistency_weight: float = 1.0
    model_weight: float = 1.0
    augmentation_likelihood_weight: float = 1.0


TUNE_DEFAULT_PRESET = TuneLlmTtaWeightPreset("default", 1.0, 1.0, 1.0)
TUNE_AGREE_MORE_PRESET = TuneLlmTtaWeightPreset("agree_more", 2.0, 1.0, 1.0)
TUNE_MODEL_HEAVY_PRESET = TuneLlmTtaWeightPreset("model_heavy", 1.0, 2.0, 0.5)


def tune_list_builtin_presets() -> tuple[TuneLlmTtaWeightPreset, ...]:
    return (TUNE_DEFAULT_PRESET, TUNE_AGREE_MORE_PRESET, TUNE_MODEL_HEAVY_PRESET)
