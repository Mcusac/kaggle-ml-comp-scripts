"""Trainer factory for contest pipelines. FeatureExtractionTrainer is defined in infra.level_2."""

from layers.layer_1_competition.level_0_infra.level_2 import FeatureExtractionTrainer

from .factory import create_trainer

__all__ = [
    "create_trainer",
    "FeatureExtractionTrainer",
]
