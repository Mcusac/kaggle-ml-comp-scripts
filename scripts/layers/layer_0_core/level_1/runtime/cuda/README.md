# level_1/runtime/cuda

## Purpose

CUDA-specific memory management and GPU monitoring utilities. Provides cleanup operations and memory statistics.

## Contents

- **gpu_cleanup.py** — GPU memory cleanup operations (cache clearing, synchronization).
- **memory.py** — Memory statistics and estimation functions.
- **monitoring.py** — GPU memory status logging.

## Public API

### Memory Cleanup

- `cleanup_gpu_memory()` — Clear CUDA cache and synchronize (single pass)
- `perform_aggressive_cleanup()` — Repeated cleanup for severe OOM scenarios (5 passes)

### Memory Statistics

- `get_model_memory_usage()` — Get GPU memory currently allocated in MB
- `estimate_memory_mb(array: np.ndarray)` — Estimate numpy array memory usage in MB
- `get_available_memory_mb()` — Get available system memory in MB
- `get_total_memory_mb()` — Get total system memory in MB
- `get_memory_usage_percent()` — Get system memory usage percentage

### Monitoring

- `print_gpu_memory_status()` — Log detailed GPU memory statistics

## Dependencies

- `level_0` — `get_logger`, `get_torch`, `is_torch_available`
- **psutil** — System memory queries

## Usage Example

```python
from layers.layer_0_core.level_1.runtime.cuda import print_gpu_memory_status, get_model_memory_usage, cleanup_gpu_memory

print_gpu_memory_status()
used_mb = get_model_memory_usage()
cleanup_gpu_memory()
```