# export

## Purpose

Model export pipeline and atomic operations for copying checkpoints and writing metadata.

## Contents

- **export_pipeline.py**: ExportPipeline
- **operations.py**: find_trained_model_path, export_from_training_dir, copy_model_checkpoint, write_metadata_file

## Public API

- `ExportPipeline` — BasePipeline for exporting models with metadata
- `find_trained_model_path(model_dir, best_fold=None)` — Find best checkpoint (PyTorch or regression)
- `export_from_training_dir(model_dir, export_dir, metadata)` — Export from fold structure to flat export
- `copy_model_checkpoint(source, dest)` — Atomic copy
- `write_metadata_file(metadata, dest)` — Write JSON metadata

## Dependencies

- level_0: ensure_dir, get_logger
- level_1: BasePipeline, validate_config_section_exists
- level_4: save_json, load_json

## Usage Example

```python
from level_5 import ExportPipeline, find_trained_model_path, export_from_training_dir
from pathlib import Path

path, fold = find_trained_model_path(Path("output/models/best_training"))
export_from_training_dir(
    Path("output/models/best_training"),
    Path("output/exports/best"),
    {"best_fold": fold, "model_name": "resnet50"},
)

pipeline = ExportPipeline(config, str(path), export_dir="exports")
pipeline.setup()
result = pipeline.execute()
```
