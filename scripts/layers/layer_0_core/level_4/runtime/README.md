# level_4.runtime

## Purpose

Unified progress tracking for training and inference. Coordinates progress bars, metrics, and formatting.

## Contents

| Module | Description |
|--------|-------------|
| progress_tracker | ProgressTracker |

## Public API

| Export | Description |
|--------|-------------|
| ProgressTracker | Progress bar and metrics tracking |

## Dependencies

- **level_0** — get_logger
- **level_1** — ProgressConfig, get_device_info
- **level_2** — ProgressMetrics, ProgressBarManager
- **level_3** — ProgressFormatter

## Usage Example

```python
from layers.layer_0_core.level_4 import ProgressTracker
from layers.layer_0_core.level_1 import ProgressConfig

config = ProgressConfig(verbosity=...)
tracker = ProgressTracker(config)
tracker.create_bar("epoch", total=100, desc="Training")
tracker.update("epoch", n=1, loss=0.5)
tracker.close_all()
```
