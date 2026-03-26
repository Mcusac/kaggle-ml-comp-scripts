# level_3 runtime

## Purpose

Runtime validation utilities for file paths and image paths in dataframes.

## Contents

- `path_validation.py` — four public validators for file existence, file-vs-directory checks, image path validation, and bulk image path validation over a DataFrame column.

## Public API

- `validate_file_exists(path, name)` — raise `DataValidationError` or `FileNotFoundError` if the path is absent; return a `Path` object on success.
- `validate_path_is_file(path, name)` — additionally assert the path resolves to a file, not a directory.
- `validate_image_path(path, check_exists, name)` — validate a single image path with optional existence check.
- `validate_image_paths_in_dataframe(df, image_column, check_exists, max_missing_to_show, name)` — validate an entire DataFrame column of image paths; reports up to `max_missing_to_show` missing files.

## Dependencies

- **level_0** — `DataValidationError` for consistent error reporting.
- **level_2** — `validate_dataframe`, `validate_column_values` for DataFrame structural checks.

## Usage Example

```python
from level_3.runtime import validate_image_paths_in_dataframe, validate_path_is_file

validate_path_is_file("config.yaml", "config")
validate_image_paths_in_dataframe(
    df=train_df,
    image_column="image_path",
    check_exists=True,
    name="training data",
)
```
