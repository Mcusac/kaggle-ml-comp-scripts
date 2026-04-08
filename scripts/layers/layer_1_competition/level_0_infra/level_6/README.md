"""Competition infra tier 6: submission builders built on infra tier 5 helpers."""

## Purpose

Owns small, reusable submission builders that coordinate feature extraction, prediction, and submission serialization.

## Contents

- `submission/`: Submission-building entrypoints (currently regression-based).

## Public API

- `create_regression_submission`: Build a regression-model submission (extract features → predict → expand → save CSV).

## Dependencies

- `level_0`: logging (`get_logger`).
- `level_4`: model loading (`load_pickle`).
- `level_5`: submission IO (`save_submission_csv`).
- `layers.layer_1_competition.level_0_infra.level_2`: feature extraction for test data (`extract_test_features_from_model`).
- `layers.layer_1_competition.level_0_infra.level_5`: post-processing to submission format (`expand_predictions_to_submission_format`).

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_6 import create_regression_submission

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

