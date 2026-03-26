"""Contest abstractions: protocols implemented by contest packages under ``contests/``."""

from pathlib import Path
from typing import Any, Optional, Protocol, Tuple


class ContestPipelineProtocol(Protocol):
    """Protocol for contest train/submit/tune pipelines."""

    def train_pipeline(self, data_root: str, **kwargs: Any) -> Optional[Path]:
        """Run training. Returns output path or None."""
        ...

    def submit_pipeline(
        self, data_root: str, strategy: str, **kwargs: Any
    ) -> Path:
        """Generate submission. Returns path to submission file."""
        ...

    def tune_pipeline(
        self, data_root: str, **kwargs: Any
    ) -> Optional[Path]:
        """Run hyperparameter tuning. Returns output path or None. Optional."""
        ...


class ContestInputValidator(Protocol):
    """Protocol for contest input validation."""

    def validate_inputs(self, data_root: str, **kwargs: Any) -> None:
        """Validate inputs. Raises on failure."""
        ...


class ContestMetric(Protocol):
    """Protocol for contest metric computation."""

    def compute(
        self,
        y_pred: Any,
        y_true: Any,
        config: Optional[Any] = None,
        **kwargs: Any,
    ) -> Tuple[float, Any]:
        """Compute metric. Returns (score, details)."""
        ...
