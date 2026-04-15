# training

Full training loop components: executors, epoch runners, checkpointing, optimizer/scheduler factories, and memory management.

## Purpose

Provides the composable pieces needed to implement a training loop: a training phase executor, a validation phase executor, simple supervised epoch templates, a model checkpointer, component factories, and memory/OOM recovery utilities.

## Contents

- `checkpointer.py` — `ModelCheckpointer`: saves and loads model checkpoints with fold/epoch tracking
- `component_factories.py` — `create_optimizer`, `create_scheduler`, `create_loss_function`
- `epoch_finalization.py` — `finalize_epoch`: log epoch results and step the scheduler
- `epoch_runners.py` — `run_train_epoch`, `run_validate_epoch`: simple supervised (X, y) epoch templates
- `multitask_config.py` — `MultiTaskTrainingConfig`: configuration for multi-task training setups
- `training_executor.py` — `TrainingPhaseExecutor`: runs the training phase with AMP support
- `validation_executor.py` — `ValidationPhaseExecutor`: runs the validation phase and computes metrics
- `memory/` — OOM recovery and resource cleanup (see sub-package)

## Public API

- `ModelCheckpointer` — Save/load model checkpoints keyed by fold and epoch
- `create_optimizer(model, config)` — Construct an optimizer from config
- `create_scheduler(optimizer, config)` — Construct an LR scheduler from config
- `create_loss_function(config)` — Construct a loss function from config
- `finalize_epoch(epoch, history, scheduler, logger)` — Log epoch metrics and step the scheduler
- `run_train_epoch(model, train_loader, optimizer, criterion, device, scaler, use_tqdm)` — Run one supervised training epoch; returns average loss
- `run_validate_epoch(model, val_loader, criterion, device, use_tqdm)` — Run one supervised validation epoch; returns average loss
- `MultiTaskTrainingConfig` — Dataclass for multi-task training parameters
- `TrainingPhaseExecutor` — Stateful executor for the training phase with AMP scaler support
- `ValidationPhaseExecutor` — Stateful executor for the validation phase with injected metric calculator
- `is_oom_error`, `recover_from_oom`, `cleanup_model`, `release_training_resources` — From `training.memory`

## Dependencies

- **level_0** — `get_logger`, `get_torch`, `get_config_value`, `step_scheduler`, `create_history_entry`
- **level_1** — `train_one_epoch`, `run_supervised_batch`, `load_model_checkpoint`, `log_epoch_progress`, `TrainingConfig`, `is_cuda_available`, `perform_aggressive_cleanup`

## Usage Example

```python
import torch
from layers.layer_0_core.level_2.training import TrainingPhaseExecutor, ValidationPhaseExecutor

train_executor = TrainingPhaseExecutor(model=model, device=device, optimizer=optimizer, criterion=criterion, config=config)
val_executor = ValidationPhaseExecutor(model=model, device=device, criterion=criterion, config=config, metric_calculator=my_metrics_fn)

for epoch in range(config.num_epochs):
    train_loss = train_executor.train(train_loader)
    val_loss, r2, r2_per_target = val_executor.validate(val_loader)
```
