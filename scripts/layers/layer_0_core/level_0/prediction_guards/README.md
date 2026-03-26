# Prediction Guards

Validation utilities for model prediction arrays and export files.

## Purpose

Ensures prediction arrays and lists are well-formed before downstream scoring or ensembling, and verifies that exported model files are present on disk.

## Contents

- `arrays.py` – Shape and target validation for single prediction arrays
- `lists.py` – Validation for lists of prediction arrays (consistent shapes, target counts)
- `policies.py` – `NonNegativePredictionMixin` for postprocessing predictions
- `submission.py` – Submission format and GO term validation
- `verify_export_files.py` – Check for required model files in an export directory

## Public API

- `validate_predictions_shape(predictions)` – Raise if predictions array is not 2-D
- `validate_targets(targets)` – Raise if targets array has unexpected shape or dtype
- `validate_predictions_list(predictions_list)` – Raise if any array in the list is malformed
- `validate_same_shape(predictions_list)` – Raise if arrays in the list differ in shape
- `get_shape_and_targets(predictions_list)` – Return (samples, targets) shape and number of targets
- `NonNegativePredictionMixin` – Mixin that clamps predictions to non-negative values
- `validate_submission_format(submission)` – Raise if submission format is invalid
- `validate_go_term_format(go_term)` – Raise if GO term string format is invalid
- `is_valid_score(score)` – Return True if score is a valid numeric value
- `verify_export_files(export_dir, model_type)` – Return dict with `success`, `message`, and `model_path`

## Dependencies

- stdlib: pathlib, typing
- numpy

## Usage Example

```python
from level_0 import validate_predictions_list, verify_export_files

validate_predictions_list(predictions)
result = verify_export_files("output/", model_type="end_to_end")
if result["success"]:
    print(result["model_path"])
```
