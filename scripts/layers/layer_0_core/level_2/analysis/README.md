# analysis

Cross-validation analysis utilities for evaluating fold score distributions and detecting CV-to-test gap issues.

## Purpose

Provides diagnostic functions for interpreting cross-validation results: identifying the best fold, analyzing test gap magnitude, and computing fold score range statistics.

## Contents

- `cv_analysis.py` — `find_best_fold_from_scores`, `analyze_cv_test_gap`, `analyze_fold_score_range`

## Public API

- `find_best_fold_from_scores(fold_scores)` — Return the fold index with the best score
- `analyze_cv_test_gap(cv_score, fold_scores, test_score=None, threshold)` — Log and return whether the CV-to-test gap exceeds the threshold
- `analyze_fold_score_range(fold_scores)` — Compute and log the min/max/range of fold scores

## Dependencies

- **level_0** — `get_logger`
- **level_1** — `calculate_fold_statistics`, `generate_cv_test_gap_warnings`

## Usage Example

```python
from layers.layer_0_core.level_2.analysis import find_best_fold_from_scores, analyze_cv_test_gap

fold_scores = [0.82, 0.85, 0.83, 0.81, 0.84]
best_fold = find_best_fold_from_scores(fold_scores)
analyze_cv_test_gap(cv_score=0.83, test_score=0.76, threshold=0.05)
```
