# infra/level_3/submission — Regression submission pipeline

**On disk:** `…/level_0_infra/level_3/submission/`. **Imports:** Call sites typically use `layers.layer_1_competition.level_0_infra.level_2` for the symbols in **Usage Example** (re-exports per `python-import-surfaces.mdc`).

## Purpose

Expand primary predictions to full submission format, save CSV, and create end-to-end regression submissions with feature extraction.

## Contents

| Module | Description |
|--------|-------------|
| `pipeline` | expand_predictions_to_submission_format, save_submission, create_regression_submission |

## Public API

- **expand_predictions_to_submission_format** — Expand primary predictions to all targets, apply post-processing, build submission rows
- **save_submission** — Save submission DataFrame to CSV (writes to /kaggle/working on Kaggle if needed)
- **create_regression_submission** — Load regression model, extract test features, predict, expand, save

## Dependencies

- **level_0:** get_logger, is_kaggle
- **level_1:** resolve_environment_path
- **level_4:** load_pickle (`create_regression_submission` path)
- **level_5:** load_and_validate_test_data
- **layers.layer_1_competition.level_0_infra.level_2.feature_extraction.test_extractor:** extract_test_features_from_model

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_2 import (
    expand_predictions_to_submission_format,
    save_submission,
    create_regression_submission,
)

# Expand and save
df = expand_predictions_to_submission_format(
    predictions,
    test_csv_path,
    contest_config=config,
    data_schema=data_schema,
    post_processor=post_processor,
)
save_submission(df, output_path)

# Or end-to-end
create_regression_submission(
    regression_model_path=model_path,
    feature_extraction_model_name="dinov2_base",
    test_csv_path=test_csv_path,
    data_root=data_root,
    config=config,
    device=device,
    output_path=output_path,
    data_schema=data_schema,
    post_processor=post_processor,
)
```
