# RNA3D level_0

## Purpose

Base layer for the Stanford RNA 3D Folding Part 2 Kaggle competition. Provides contest configuration, data schema, paths, post-processing, train-label grouping, validation, prediction artifacts, and notebook command builders. **TM-score scoring** (`evaluate_predictions_tm`, `TargetTMScore`, etc.) lives in **`level_1.scoring`** and is exported from `layers.layer_1_competition.level_1_impl.level_rna3d.level_1`.

## Contents

- **config.py** — RNA3DConfig extending ContestConfig; minimal target interface for coordinate submissions
- **data_schema.py** — RNA3DDataSchema and build_coordinate_columns for submission column names
- **paths.py** — RNA3DPaths for competition data paths
- **post_processor.py** — RNA3DPostProcessor clips coordinates to valid PDB range
- **train_labels.py** — group_labels_by_target for train_labels.csv ID parsing and grouping
- **validate_data.py** — validate_rna3d_inputs for CSV presence and schema checks
- **artifacts.py** — PredictionArtifact dataclass and save/load helpers
- **notebook_commands.py** — build_*_command for validate_data, train, tune, submit

## Public API

Aligned with `level_0/__init__.py` `__all__`:

| Name | Description |
|------|-------------|
| RNA3DConfig | Contest configuration with empty target interface |
| RNA3DDataSchema | Schema for sequences and labels CSVs |
| build_coordinate_columns | Build x_k,y_k,z_k column names for n structures |
| RNA3DPaths | Path constants for stanford-rna-3d-folding-2 |
| RNA3DPostProcessor | Clips predictions to [-999.999, 9999.999] |
| group_labels_by_target | Split train_labels rows by target_id from ID column |
| validate_rna3d_inputs | Validate CSV inputs and schema |
| ARTIFACT_VERSION | Prediction artifact format version |
| PredictionArtifact | Container for predictions and metadata |
| load_prediction_artifact | Load artifact from pickle |
| save_prediction_artifact | Save artifact to pickle |
| build_validate_data_command | Command list for run.py validate_data |
| build_train_command | Command list for run.py train |
| build_tune_command | Command list for run.py tune |
| build_submit_command | Command list for run.py submit |

## Dependencies

- **layers.layer_1_competition.level_0_infra.level_0** — ContestConfig, ContestDataSchema, ContestPaths, ClipRangePostProcessor
- **layers.layer_1_competition.level_0_infra.level_1** — `get_data_root_path`, `get_run_py_path` (notebook commands)
- **level_0** — get_logger (project foundation)
- **level_4** — PICKLE_HIGHEST_PROTOCOL, load_pickle, save_pickle (artifacts)

## Usage Example

```python
import numpy as np
import pandas as pd

from layers.layer_1_competition.level_1_impl.level_rna3d.level_0 import (
    RNA3DConfig,
    RNA3DPaths,
    RNA3DPostProcessor,
    build_coordinate_columns,
)
from layers.layer_1_competition.level_1_impl.level_rna3d.level_1 import evaluate_predictions_tm

_ = RNA3DConfig()
paths = RNA3DPaths()
_ = paths.kaggle_dataset_name
processor = RNA3DPostProcessor()
cols = build_coordinate_columns(n_structures=5)

L, K = 4, 2
pred = np.zeros((L, K, 3), dtype=np.float32)
labels = pd.DataFrame(
    {
        "ID": [f"t1_{i}" for i in range(L)],
        "resid": list(range(L)),
        "x_1": np.zeros(L, dtype=np.float32),
        "y_1": np.zeros(L, dtype=np.float32),
        "z_1": np.zeros(L, dtype=np.float32),
    }
)
mean_tm, per_target = evaluate_predictions_tm({"t1": pred}, labels)
```

To validate on-disk competition CSVs (requires data under `paths.local_data_path`):

```python
from layers.layer_1_competition.level_1_impl.level_rna3d.level_0 import RNA3DPaths, validate_rna3d_inputs

validate_rna3d_inputs(RNA3DPaths().local_data_path)
```
