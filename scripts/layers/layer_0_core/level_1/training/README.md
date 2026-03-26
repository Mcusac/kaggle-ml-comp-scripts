# training

## Purpose
Framework-level training primitives: checkpoint persistence, epoch execution loops, mixed precision setup, and generic model I/O.

## Contents
- `batch_processor.py` — `run_supervised_batch`: supervised training step
- `checkpoint.py` — `save_checkpoint`, `load_model_checkpoint`
- `config_helper.py` — `extract_config_settings`, `get_required_config_value`, `get_training_config_value`, `ConfigHelper`
- `epochs/` — `train_one_epoch`, `log_epoch_progress`, `log_epoch_progress_with_metric`
- `forward_pass.py` — `forward_with_amp`: forward pass with optional AMP autocast
- `model_io.py` — `save_regression_model`, `save_vision_model`, `load_vision_model`
- `setup.py` — `setup_mixed_precision`: creates GradScaler if AMP is enabled

## Public API
- `train_one_epoch(train_loader, batch_processor, optimizer, scaler, use_tqdm, tqdm_desc)` → float
- `log_epoch_progress(*, epoch, num_epochs, train_loss, val_loss, metric_name, metric_value, optimizer, log_interval)` → None
- `log_epoch_progress_with_metric(*, ...)` → None
- `run_supervised_batch(model, device, criterion, batch)` → tuple
- `save_checkpoint(model, optimizer, scheduler, path, epoch, best_score, history)` → None
- `load_model_checkpoint(checkpoint_path, model, optimizer, scheduler, device)` → dict
- `extract_config_settings(config, num_primary_targets, model_name, image_size)` → tuple
- `get_required_config_value(config, key, *, error_msg)` → value
- `get_training_config_value(config, key, default)` → value
- `forward_with_amp(model, inputs, use_amp)` → tensor
- `save_regression_model(model, save_dir)` → None
- `save_vision_model(model, path)` → None
- `load_vision_model(model, path, device)` → None
- `setup_mixed_precision(config, device)` → (use_amp: bool, scaler)

## Dependencies
- `level_0` — `ensure_dir`, `get_logger`, `get_torch`, `get_config_value`, `extract_batch_data`

## Usage Example
```python
from level_1.training import save_checkpoint, load_model_checkpoint, train_one_epoch
save_checkpoint(model, optimizer, scheduler, path=Path("ckpt.pth"), epoch=5, best_score=0.84, history=[])
```