# level_3 ensemble_strategies

## Purpose

Console and log post-processors for ensemble and stacking CLI/subprocess outcomes: they normalize completion banners and next-step hints via `log_pipeline_completion` from layers.layer_0_core.level_2.

## Contents

- `handle_regression_ensemble_result.py` — Logs regression-ensemble runs from return code, stdout tail, and config.
- `handle_stacking_results.py` — `handle_stacking_result` and `handle_hybrid_stacking_result` for stacking and hybrid stacking pipelines.
- `pipeline_result_handler.py` — `handle_ensemble_result` for generic ensemble completion (includes submission path footer).

## Public API

- `handle_regression_ensemble_result(returncode, stdout_lines, log_file, ensemble_config)` — Emit structured log lines after a regression ensemble finishes.
- `handle_stacking_result(...)` — Same pattern for stacking; accepts an `operation_name` label.
- `handle_hybrid_stacking_result(...)` — Hybrid stacking variant with dedicated config messaging.
- `handle_ensemble_result(returncode, stdout_lines, log_file, model_paths, method, score_type, model)` — Ensemble pipeline completion with model metadata.

## Dependencies

- **level_1** — `get_default_submission_csv_path` (ensemble handler footer).
- **level_2** — `log_pipeline_completion` for consistent success/failure banners.

## Usage Example

```python
from layers.layer_0_core.level_3 import handle_ensemble_result

handle_ensemble_result(
    returncode=0,
    stdout_lines=[],
    log_file="/tmp/ensemble.log",
    model_paths=["/models/a.pt", "/models/b.pt"],
    method="weighted",
    score_type="rmse",
    model="efficientnet_b0",
)
```
