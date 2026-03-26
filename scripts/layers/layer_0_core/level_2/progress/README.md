# progress

Progress bar management and timing metrics for training loops.

## Purpose

Provides tqdm-based progress bar lifecycle management and a timing/throughput tracker that supports ETA estimation and optional memory info injection.

## Contents

- `bar_manager.py` — `ProgressBarManager`: creates, tracks, and closes tqdm progress bars with hierarchical level positioning
- `metrics_calculator.py` — `ProgressMetrics`: tracks per-bar timing, rate, throughput, ETA, and elapsed time

## Public API

- `ProgressBarManager` — Manages multiple tqdm bars identified by string IDs; respects `ProgressVerbosity` to suppress display
- `ProgressMetrics` — Stateful per-bar timing tracker; supports `register_bar`, `record_update`, `estimate_eta`, `calculate_throughput`, `get_elapsed_time`, `get_memory_info`

## Dependencies

- **level_1** — `ProgressVerbosity` (for conditional display in `ProgressBarManager`), `ProgressConfig` (injected into `ProgressMetrics`)

## Usage Example

```python
from level_1 import ProgressConfig, ProgressVerbosity
from level_2.progress import ProgressBarManager, ProgressMetrics

config = ProgressConfig(verbosity=ProgressVerbosity.MODERATE)
metrics = ProgressMetrics(config)
manager = ProgressBarManager(verbosity=config.verbosity)

bar_id = manager.create_bar("epoch", total=50, desc="Epoch", level=1)
if bar_id:
    metrics.register_bar(bar_id)
    for i in range(50):
        metrics.record_update(bar_id, 1)
        manager.get_bar(bar_id).update(1)
    metrics.cleanup(bar_id)

manager.close_all()
```
