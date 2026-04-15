# level_3 workflows

## Purpose

Orchestration utilities for training and evaluation pipelines, including progress bar formatting and a cross-validation train-then-test pipeline.

## Contents

- `train_test_pipeline.py` — `train_test_pipeline`: runs cross-validation training via a caller-supplied pipeline function, selects the best fold, and delegates to the contest context's test pipeline.
- `progress_formatter.py` — `ProgressFormatter`: builds tqdm postfix dictionaries with ETA, throughput, and memory stats according to verbosity level.

## Public API

- `train_test_pipeline(contest_context, train_pipeline_fn, data_root, model, **kwargs)` — run full CV training + best-fold test; requires the contest to supply `contest_context` and `train_pipeline_fn`.
- `ProgressFormatter(config)` — formatter with `format_postfix(bar_id, metrics, current, total, unit, **kwargs)` and static `format_time(seconds)` methods.

## Dependencies

- **level_0** — `get_logger`, `get_fold_checkpoint_path`.
- **level_1** — `ProgressConfig`, `ProgressVerbosity`.
- **level_2** — `find_best_fold_from_scores`, `ProgressMetrics`.

## Usage Example

```python
from layers.layer_0_core.level_3.workflows import train_test_pipeline, ProgressFormatter
from layers.layer_0_core.level_1 import ProgressConfig, ProgressVerbosity

train_test_pipeline(
    contest_context=ctx,
    train_pipeline_fn=my_train_fn,
    data_root="/data",
    model="efficientnet_b2",
)

formatter = ProgressFormatter(ProgressConfig(verbosity=ProgressVerbosity.MODERATE))
postfix = formatter.format_postfix("epoch", metrics, current=10, total=100)
```
