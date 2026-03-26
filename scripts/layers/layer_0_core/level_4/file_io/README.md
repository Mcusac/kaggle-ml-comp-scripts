# level_4.file_io

## Purpose

Loading and saving for common data formats with consistent validation and error handling. Single place for file I/O patterns used across the codebase. Clear split between raw (minimal) and validated (full) operations.

## Contents

| Module | Description |
|--------|-------------|
| csv | CSV load/save with optional column and row validation |
| json | JSON load/save with optional type validation |
| yaml | YAML load/save |
| pickle | Pickle load/save |
| images | Image load/save via PIL |
| memmap | Memory-mapped arrays for large datasets |

## Public API

| Export | Description |
|--------|-------------|
| load_csv_raw, load_csv, save_csv | CSV I/O |
| load_json_raw, load_json, save_json | JSON I/O |
| load_yaml_raw, load_yaml, save_yaml | YAML I/O |
| load_pickle_raw, load_pickle, save_pickle | Pickle I/O |
| load_image_raw, load_image, save_image | Image I/O |
| should_use_memmap, create_memmap, load_memmap | Memmap utilities |
| save_memmap_with_metadata, load_memmap_with_metadata, MEMMAP_THRESHOLD_MB | Memmap with metadata |

## Dependencies

- **level_0** — get_logger, DataLoadError, DataValidationError, DataProcessingError, ensure_dir, load_image_pil
- **level_2** — validate_dataframe (csv only)
- **level_3** — validate_path_is_file

## Usage Example

```python
from level_4 import load_csv, load_yaml, save_pickle

df = load_csv("data/train.csv", required_cols=["id", "target"])
config = load_yaml("config.yaml")
save_pickle(model, "output/model.pkl")
```
