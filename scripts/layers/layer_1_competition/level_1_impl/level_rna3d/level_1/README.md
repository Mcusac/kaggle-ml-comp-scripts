# RNA3D level_1

## Purpose

Provides the RNA3D **baseline approximation** pipeline: template selection via alignment, coordinate adaptation, optional backbone smoothing, and writing `submission.csv` in the competition format.

## Contents

- **baseline_approx.py** — `BaselineApproxConfig`, `BaselineApproxPredictor`, internal `Template` dataclass, label grouping, template building, prediction batching, CSV formatting, and `make_submission` entry point.

## Public API

| Name | Description |
|------|-------------|
| BaselineApproxConfig | Frozen dataclass of tunable baseline parameters (structures count, alignment, noise, smoke `max_targets`). |
| BaselineApproxPredictor | Builds multiple (L,3) structures per sequence from a template bank. |
| build_templates | Builds `Template` rows from train sequences and a target-id → coords map. |
| group_labels_to_coords | Maps `train_labels.csv` rows to per-target coordinate arrays (first conformation x_1,y_1,z_1). |
| run_baseline_approx_predictions | Runs the predictor over a `sequences_df` for a given `data_root` and config. |
| format_predictions_to_submission_csv | Turns prediction dicts into a submission DataFrame/CSV with post-processing. |
| make_submission | End-to-end: reads train/test CSVs under `data_root`, writes submission CSV. |

## Dependencies

- **level_0** — `get_logger`, `ensure_dir` for logging and output directories.
- **layers.layer_1_competition.level_1_impl.level_rna3d.level_0** — `build_coordinate_columns`, `RNA3DPaths`, `RNA3DPostProcessor`, `group_labels_by_target` for schema-aligned I/O and coordinate cleanup.

## Usage Example

```python
from layers.layer_1_competition.level_1_impl.level_rna3d.level_1 import BaselineApproxConfig, make_submission

# data_root must contain train_sequences.csv, train_labels.csv, and test_sequences.csv
out_path = make_submission(
    "/path/to/rna3d/data",
    BaselineApproxConfig(max_targets=5),  # limit targets for a quick smoke run; 0 = all
)
print(out_path)
```
