"""Regression submission builder(s) for competition infra tier 6."""

## Purpose

Provides submission builders that take a trained regression model and produce a valid submission CSV.

## Contents

- `regression_submission.py`: Extract test features, run regression predictions, expand to submission format, and write CSV output.

## Public API

- `create_regression_submission`: End-to-end submission creation for a regression model.

## Dependencies

- `level_0`: logging (`get_logger`).
- `level_4`: model loading (`load_pickle`).
- `level_5`: submission IO (`save_submission_csv`).
- `layers.layer_1_competition.level_0_infra.level_2`: feature extraction (`extract_test_features_from_model`).
- `layers.layer_1_competition.level_0_infra.level_5`: submission formatting (`expand_predictions_to_submission_format`).

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_6.submission import (
    create_regression_submission,
)

create_regression_submission(
    regression_model_path="path/to/regression_model.pkl",
    feature_extraction_model_name="resnet18",
    test_csv_path="input/test.csv",
    data_root="input/",
    config=contest_config,
    device=device,
    output_path="submission.csv",
    data_schema=contest_data_schema,
    post_processor=contest_post_processor,
)
```

