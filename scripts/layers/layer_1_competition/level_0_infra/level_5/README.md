## Purpose
Competition infra tier 5 focuses on submission formatting for contest code, built on lower-level core IO/data loading utilities.

## Contents
- `submission/`: build a submission `DataFrame` from model predictions.

## Public API
- `expand_predictions_to_submission_format`: convert primary predictions into the final submission row format.

## Dependencies
- `level_0`: logging (`get_logger`).
- `level_5`: validate/load test CSV rows used to align predictions (`load_and_validate_test_data`).

## Usage Example
```python
import numpy as np

from layers.layer_1_competition.level_0_infra.level_5 import (
    expand_predictions_to_submission_format,
)

df = expand_predictions_to_submission_format(
    predictions=np.zeros((10, 3), dtype=np.float32),
    test_csv_path="input/my_contest/test.csv",
    contest_config=contest_config,
    data_schema=data_schema,
    post_processor=post_processor,
)
```
