"""Shared configuration base for all domains (tabular, vision)."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class BaseConfig:
    """
    Root configuration type for the framework.
    All domain configs (tabular, vision) inherit from this.
    Provides a common type for isinstance checks and future shared fields.
    Subclasses must not add mutable default fields without field(default_factory=...).
    """
    pass


@dataclass
class TrainingSchema:
    """Shared training configuration."""
    batch_size: int = 32
    epochs: int = 30
    learning_rate: Optional[float] = None


@dataclass
class EvaluationSchema:
    """Shared evaluation configuration."""
    metric: str = ""  # Must be set by domain config subclass


@dataclass
class PathConfig:
    """Shared path configuration."""
    output_dir: Path = field(default_factory=lambda: Path("output"))
    checkpoint_dir: Path = field(default_factory=lambda: Path("checkpoints"))


@dataclass
class CompositeConfig(BaseConfig):
    """Base for TabularConfig/VisionConfig. Subclasses add model, data, and domain validation."""

    training: TrainingSchema = field(default_factory=TrainingSchema)
    evaluation: EvaluationSchema = field(default_factory=EvaluationSchema)
    paths: PathConfig = field(default_factory=PathConfig)
