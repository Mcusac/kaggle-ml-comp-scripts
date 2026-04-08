"""Vision domain configuration."""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from level_0 import (
    CompositeConfig,
    EvaluationSchema,
    PathConfig,
    TrainingSchema,
)


@dataclass
class VisionModelConfig:
    """Vision model configuration."""
    name: str = "efficientnet_b0"
    type: str = "vision"
    num_classes: int = 1
    pretrained: bool = True
    input_size: Optional[Tuple[int, int]] = None
    use_tiles: bool = False
    tile_grid_size: int = 3
    hidden_size: Optional[int] = None
    dropout_rate: float = 0.3

    def __post_init__(self):
        if self.num_classes <= 0:
            raise ValueError("num_classes must be positive")


@dataclass
class VisionDataConfig:
    """Vision data configuration."""
    image_size: int = 224
    augmentation: str = "medium"
    preprocessing: List[str] = field(default_factory=lambda: ["resize", "normalize"])
    augmentation_list: List[str] = field(
        default_factory=lambda: ["geometric", "color_jitter"]
    )
    use_tta: bool = False
    tta_variants: List[str] = field(
        default_factory=lambda: ["original", "h_flip"]
    )

    def __post_init__(self):
        if self.image_size <= 0:
            raise ValueError("image_size must be positive")


def _default_training() -> TrainingSchema:
    return TrainingSchema(
        batch_size=32,
        epochs=30,
        learning_rate=1e-4,
    )


def _default_evaluation() -> EvaluationSchema:
    return EvaluationSchema(metric="accuracy")


@dataclass
class VisionConfig(CompositeConfig):
    """Complete configuration for vision tasks."""
    model: VisionModelConfig = field(default_factory=VisionModelConfig)
    data: VisionDataConfig = field(default_factory=VisionDataConfig)
    training: TrainingSchema = field(default_factory=_default_training)
    evaluation: EvaluationSchema = field(default_factory=_default_evaluation)
    paths: PathConfig = field(default_factory=PathConfig)