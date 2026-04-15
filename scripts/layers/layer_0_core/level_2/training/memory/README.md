# training/memory

GPU memory management: OOM detection, recovery, and resource cleanup.

## Purpose

Provides utilities to detect and recover from out-of-memory errors during training, and to release GPU/CPU resources after training completes.

## Contents

- `oom_recovery.py` — `is_oom_error`, `recover_from_oom`: OOM detection and multi-step recovery
- `resource_cleanup.py` — `cleanup_model`, `release_training_resources`: model and training resource teardown

## Public API

- `is_oom_error(exception)` — Return True if the exception is a CUDA out-of-memory error
- `recover_from_oom(model, delay_seconds, cleanup_passes)` — Attempt to recover from OOM by clearing CUDA cache and running garbage collection
- `cleanup_model(model)` — Move model to CPU and delete it to free GPU memory
- `release_training_resources(dataframe, dataset, dataloader, model, aggressive, delay_seconds)` — Release training objects and flush CUDA cache

## Dependencies

- **level_0** — `get_logger`, `get_torch`
- **level_1** — `is_cuda_available`, `perform_aggressive_cleanup`

**Note:** `release_training_resources` uses `dataloader._iterator` (private PyTorch attribute) to shut down worker processes when a dataloader is passed. This is best-effort and may break across PyTorch versions.

## Usage Example

```python
from layers.layer_0_core.level_2.training import is_oom_error, recover_from_oom

try:
    loss = criterion(model(inputs), targets)
    loss.backward()
except RuntimeError as e:
    if is_oom_error(e):
        recover_from_oom(model, optimizer)
    else:
        raise
```
