# level_1/io

## Purpose
Submission file formatting, sorting, and prediction limit enforcement for TSV submission files.

## Contents
- `tsv_submission_formatter.py` — `TsvSubmissionFormatter`: configurable TSV parser, external sort, top-K per ID enforcement

## Public API
- `TsvSubmissionFormatter(parse_line, score_min, score_max)` — Formatter with optional custom parse logic

## Dependencies
- `level_0` — `get_logger`

## Usage Example
```python
from level_1.io import TsvSubmissionFormatter

formatter = TsvSubmissionFormatter(score_min=0.0, score_max=1.0)
formatter.sort_submission_external("raw.tsv", "sorted.tsv")
formatter.enforce_prediction_limits("sorted.tsv", max_predictions_per_id=1500)
```
