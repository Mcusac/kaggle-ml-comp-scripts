"""Path-returning ARC pipeline stages (train / tune / submit).

Subpackage replaces the monolithic ``stages.py``. Re-exports the three public
stage entry points so both direct imports (``from ...level_5.stages import
run_train_pipeline``) and the ``test_arc_agi_2_validate_pipeline.py`` string
mock target (``layers...level_5.stages.run_train_pipeline``) continue to
resolve unchanged.
"""

from .submit import run_submission_pipeline
from .train import run_train_pipeline
from .tune import run_tune_pipeline

__all__ = [
    "run_train_pipeline",
    "run_tune_pipeline",
    "run_submission_pipeline",
]
