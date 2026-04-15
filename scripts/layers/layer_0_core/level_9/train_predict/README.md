# level_9.train_predict

## Purpose

Train-then-predict workflow that composes TrainPipeline and PredictPipeline for a single train-and-predict run.

## Contents

| Module | Description |
|--------|-------------|
| `workflow.py` | TrainPredictWorkflow class |

## Public API

| Name | Description |
|------|-------------|
| `TrainPredictWorkflow` | Workflow that trains a model then generates predictions on test data |

## Dependencies

- **level_0**: get_logger
- **level_1**: BasePipeline
- **level_6**: PredictPipeline
- **level_8**: TrainPipeline

## Usage Example

```python
from layers.layer_0_core.level_9 import TrainPredictWorkflow

workflow = TrainPredictWorkflow(
    config=config,
    model_type="vision",
    use_tta=False,
    train_data=train_df,
    val_data=val_df,
    test_data=test_df,
    image_dir=image_dir,
)
workflow.setup()
result = workflow.execute()
# result['predictions_path'] contains output path
```

## Generated

2026-04-08 (audit pass 1).
