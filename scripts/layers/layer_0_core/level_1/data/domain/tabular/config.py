"""Tabular domain configuration."""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from level_0 import (
    CompositeConfig,
    EvaluationSchema,
    PathConfig,
    TrainingSchema,
)


@dataclass
class TabularModelConfig:
    """Tabular model configuration."""
    type: str = "logistic"
    input_dim: int = 100
    output_dim: int = 50
    hyperparameters: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.input_dim <= 0:
            raise ValueError("input_dim must be positive")
        if self.output_dim <= 0:
            raise ValueError("output_dim must be positive")


@dataclass
class TabularDataConfig:
    """Tabular data configuration."""
    feature_types: List[str] = field(default_factory=lambda: ["hand_crafted"])
    embedding_types: List[str] = field(default_factory=lambda: [])
    use_memmap: bool = True
    chunk_size: int = 10000
    validation_split: float = 0.2


def _default_training() -> TrainingSchema:
    return TrainingSchema(batch_size=64, epochs=100)


def _default_evaluation() -> EvaluationSchema:
    return EvaluationSchema(metric="f1")


@dataclass
class TabularConfig(CompositeConfig):
    """Complete configuration for tabular tasks."""
    model: TabularModelConfig = field(default_factory=TabularModelConfig)
    data: TabularDataConfig = field(default_factory=TabularDataConfig)
    training: TrainingSchema = field(default_factory=_default_training)
    evaluation: EvaluationSchema = field(default_factory=_default_evaluation)
    paths: PathConfig = field(default_factory=PathConfig)