# level_5.training

## Purpose

Training orchestration for reusable model-training workflows, including end-to-end training loops and a focused vision trainer.

## Contents

| Module | Description |
|--------|-------------|
| `base_model_trainer.py` | `BaseModelTrainer` for configurable training with helper-based phase orchestration |
| `vision_trainer.py` | `VisionTrainer` with explicit train/validate/fit loop, checkpointing, and optional mixed precision |
| `__init__.py` | Package exports |

## Public API

| Export | Description |
|--------|-------------|
| `BaseModelTrainer` | High-level trainer that composes builders/helpers for model creation, phases, checkpointing, and early stopping |
| `VisionTrainer` | Vision-focused trainer with direct control over train/validate loops and checkpoint lifecycle |

## Dependencies

- `base_model_trainer.py`
  - **level_0**: `ensure_dir`, `get_logger`, `get_torch`
  - **level_1**: `get_device`, `setup_mixed_precision`
  - **level_2**: `extract_config_settings`, `get_training_config_value`, `create_optimizer`, `create_scheduler`, `create_loss_function`, `finalize_epoch`, `TrainingPhaseHelper`, `ValidationPhaseHelper`, `ModelCheckpointer`
  - **level_4**: `create_vision_model`
- `vision_trainer.py`
  - **level_0**: `ensure_dir`, `get_logger`, `get_torch`, `extract_batch_data`
  - **level_1**: `train_one_epoch`, `load_model_checkpoint`, `forward_with_amp`
  - **level_4**: `calculate_metrics`

## Usage Example

```python
from level_5 import BaseModelTrainer, VisionTrainer

base_trainer = BaseModelTrainer(config, model_name="resnet50")
history = base_trainer.train(train_loader, val_loader, num_epochs=50, save_dir="output/models")

vision_trainer = VisionTrainer(model, criterion, optimizer, device)
result = vision_trainer.fit(train_loader, val_loader, num_epochs=10)
```
