# data/io

## Purpose
Generic file loading utilities: batch multi-file loading with error handling and numpy embedding file loading.

## Contents
- `batch_loading.py` — `BatchLoader` protocol and `load_batch` function
- `numpy_loader.py` — `load_ids_file`, `load_embeddings_file`, `build_embedding_error_message`

## Public API
- `BatchLoader` — Protocol type for callables that load lists of items from paths
- `load_batch(paths, loader, *, desc, show_progress, item_name, raise_on_error)` — applies loader to each path, returns list
- `load_ids_file(ids_path)` — loads a `.npy` IDs array
- `load_embeddings_file(embeddings_path, embedding_type, datatype, use_memmap)` — loads a `.npy` embeddings array, optionally as memmap
- `build_embedding_error_message(embedding_type, datatype, base_path, checked_paths)` — builds diagnostic error string

## Dependencies
- `level_0` — `get_logger`

## Usage Example
```python
from layers.layer_0_core.level_1.data.io import load_batch
import pandas as pd
dataframes = load_batch(csv_paths, loader=pd.read_csv, item_name="CSV files")
```