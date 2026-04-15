# validation

Input validators for arrays, DataFrames, lists, and Series.

## Purpose

Provides type-specific validation functions that raise `DataValidationError` on invalid inputs. Each module covers one data container type.

## Contents

- `arrays.py` — `validate_array`, `validate_model_output`, `validate_paired_arrays`
- `dataframes.py` — `validate_dataframe`, `validate_column_values`
- `lists.py` — `validate_list`, `validate_list_not_empty`
- `series.py` — `validate_series`

## Public API

- `validate_array(arr, name)` — Raise if arr is not a non-empty numpy array
- `validate_model_output(output, expected_shape)` — Raise if model output shape is unexpected
- `validate_paired_arrays(arr_a, arr_b, name_a, name_b)` — Raise if two arrays differ in length
- `validate_dataframe(df, name, required_cols)` — Raise if df is not a DataFrame or is missing required columns
- `validate_column_values(df, column, valid_values)` — Raise if column contains values outside the allowed set
- `validate_list(lst, name)` — Raise if lst is not a list
- `validate_list_not_empty(lst, name)` — Raise if lst is an empty list
- `validate_series(series, name)` — Raise if series is not a non-empty pandas Series

## Dependencies

- **level_0** — `DataValidationError`
- **level_1** — `check_not_none`, `check_array_finite`, `check_min_collection_length`

## Usage Example

```python
import numpy as np
from layers.layer_0_core.level_2.validation import validate_array, validate_paired_arrays

preds = np.array([0.1, 0.9, 0.5])
targets = np.array([0, 1, 1])
validate_array(preds, "predictions")
validate_paired_arrays(preds, targets, "predictions", "targets")
```
