# metadata

## Purpose

Metadata path resolution for Kaggle competitions and local mimic layouts (input/, working/).

## Contents

- **paths.py**: find_metadata_dir, get_writable_metadata_dir, load_combo_metadata

## Public API

- `find_metadata_dir(dataset_name, from_file=None)` — Find read-only metadata dir (Kaggle input/working or local)
- `get_writable_metadata_dir(dataset_name, from_file=None)` — Get writable dir, create if missing
- `load_combo_metadata(metadata_dir, subpath)` — Load JSON from metadata_dir/subpath

## Dependencies

- level_0: is_kaggle, ensure_dir
- level_4: load_json

## Usage Example

```python
from level_5 import find_metadata_dir, get_writable_metadata_dir, load_combo_metadata
from pathlib import Path

meta_dir = find_metadata_dir("csiro-metadata")
if meta_dir:
    data = load_combo_metadata(meta_dir, "data_manipulation/metadata.json")

writable = get_writable_metadata_dir("my-metadata")
```
