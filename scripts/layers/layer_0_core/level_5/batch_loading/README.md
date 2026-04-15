# batch_loading

## Purpose

Batch load CSV files and images with optional progress display, delegating to level_1.load_batch and level_4 file I/O.

## Contents

- **csv_batch.py**: load_csv_batch
- **image_batch.py**: load_image_batch

## Public API

- `load_csv_batch(paths, *, show_progress=False, **kwargs)` — Load multiple CSVs, returns List[pd.DataFrame]
- `load_image_batch(paths, *, convert_rgb=True, show_progress=False)` — Load multiple images, returns List[PIL.Image]

## Dependencies

- level_1: load_batch
- level_4: load_csv, load_image

## Usage Example

```python
from layers.layer_0_core.level_5 import load_csv_batch, load_image_batch
from pathlib import Path

csvs = load_csv_batch(Path("data").glob("*.csv"), show_progress=True)
images = load_image_batch(["img1.jpg", "img2.jpg"], convert_rgb=True)
```
