"""Evaluation configuration."""

from dataclasses import dataclass
from typing import List, Optional, Literal

from level_0 import RuntimeConfig


@dataclass
class EvaluationConfig(RuntimeConfig):
    """Evaluation metrics and settings."""
    
    # Primary metric for model selection
    primary_metric: str = 'accuracy'  # 'accuracy', 'f1', 'r2', 'mae', etc.
    
    # Additional metrics to track
    additional_metrics: Optional[List[str]] = None
    
    # Metric computation settings
    metric_average: Literal["macro", "micro", "weighted", "samples"] = "macro"    

    # Evaluation mode
    eval_batch_size: Optional[int] = None  # If None, uses training batch_size
    
    def __post_init__(self):
        if self.additional_metrics is None:
            self.additional_metrics = []
