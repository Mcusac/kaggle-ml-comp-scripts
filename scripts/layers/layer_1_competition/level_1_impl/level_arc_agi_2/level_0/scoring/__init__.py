"""ARC scoring subpackage.

Re-exports the public surface of the original `scoring.py` module so external
callers continue to work after the SRP split into:
- `grid_metrics.py` — per-grid scoring primitives
- `heuristic_scoring.py` — corpus-level heuristic scoring routines
"""

from .grid_metrics import (
    _cell_match_counts,
    eval_solution_grids_for_task,
    score_grid_exact_match,
)
from .heuristic_scoring import (
    score_heuristic_exact_match_on_training,
    score_heuristic_on_evaluation,
    score_heuristic_on_training_challenges,
)

__all__ = [
    "eval_solution_grids_for_task",
    "score_grid_exact_match",
    "score_heuristic_exact_match_on_training",
    "score_heuristic_on_evaluation",
    "score_heuristic_on_training_challenges",
]
