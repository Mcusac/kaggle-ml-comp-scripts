# level_4.pipeline

## Purpose

Pipelines for evaluation and submission averaging. Evaluates predictions (vision/tabular) and combines multiple submission files.

## Contents

| Module | Description |
|--------|-------------|
| evaluate_pipeline | EvaluatePipeline for evaluation |
| submission_averaging | SubmissionAveragingWorkflow for averaging submissions |
| threshold_optimization | optimize_threshold for multi-label classification |

## Public API

| Export | Description |
|--------|-------------|
| EvaluatePipeline | Pipeline for evaluation |
| SubmissionAveragingWorkflow | Workflow for averaging submission files |
| optimize_threshold | Optimize threshold for multi-label classification |

## Dependencies

- **level_0** — ensure_dir, get_logger, validate_submission_format
- **level_1** — BasePipeline, validate_config_section_exists
- **level_2** — simple_average, weighted_average, value_rank_average, value_percentile_average, power_average, geometric_mean, max_ensemble
- **level_3** — calculate_regression_metrics, calculate_f1, calculate_precision, calculate_recall, calculate_roc_auc

## Usage Example

```python
from layers.layer_0_core.level_4 import EvaluatePipeline, SubmissionAveragingWorkflow, optimize_threshold

pipeline = EvaluatePipeline(config, predictions=preds, ground_truth=y_true)
result = pipeline.execute()

workflow = SubmissionAveragingWorkflow(
    config, submission_files=["f1.tsv", "f2.tsv"], ensemble_method="average"
)
workflow.setup()
workflow.execute()

threshold = optimize_threshold(y_true, y_pred_proba, metric="f1")
```
