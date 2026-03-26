# Training

Training loop primitives: config building, batch extraction, epoch history, and LR scheduler stepping.

## Purpose

Provides stateless utilities used inside training loops: building config dicts, extracting batch tensors and moving them to device, recording epoch metrics, and stepping learning rate schedulers.

## Contents

- `build_config.py` – `build_training_config`: construct a training config dict from explicit parameters
- `extract_batch_data.py` – `extract_batch_data`: unpack a batch tuple and move tensors to device
- `epoch_history.py` – `create_history_entry`: create a typed epoch metrics dict
- `scheduler.py` – `get_scheduler_mode`, `step_scheduler`: read scheduler mode and advance the scheduler

## Public API

- `build_training_config(batch_size, num_epochs, learning_rate, optimizer, loss_function, scheduler, **extra)` – Return a training config dict
- `extract_batch_data(batch, device)` – Return `(inputs, targets)` with tensors on device; raises `TypeError` if batch has no `.to()` method
- `create_history_entry(epoch, train_loss, val_loss, metric, ...)` – Return a dict representing one epoch's metrics
- `get_scheduler_mode(config)` – Return `'max'` or `'min'` from config
- `step_scheduler(scheduler, config, primary_metric_value, val_loss)` – Advance scheduler using the appropriate metric

## Dependencies

- stdlib: typing

## Usage Example

```python
from level_0 import extract_batch_data, step_scheduler

inputs, targets = extract_batch_data(batch, device="cuda")
step_scheduler(scheduler, config, primary_metric_value=0.85, val_loss=0.12)
```
