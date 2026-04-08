# metadata

## Purpose

Metadata path resolution for Kaggle competitions and local mimic layouts (input/, working/).

## Contents

- **paths.py**: project/input discovery, metadata directory resolution, combo JSON loading
- **scores.py**: best-fold and score extraction from training JSON

## Public API

- `find_project_input_root(from_file)` — Resolve `input/` root for local mimic layouts
- `find_metadata_dir(dataset_name, from_file=None)` — Find read-only metadata dir (Kaggle input/working or local)
- `get_writable_metadata_dir(dataset_name, from_file=None)` — Get writable dir, create if missing
- `load_combo_metadata(metadata_dir, subpath)` — Load JSON from metadata_dir/subpath
- `extract_scores_from_json(...)` — Read metric rows and best fold from a model JSON
- `resolve_best_fold_and_score(...)` — Pick final best fold and score from extracted data

## Dependencies

- **level_0**: `is_kaggle`, `ensure_dir`, `get_logger`
- **level_4**: `load_json`, `load_json_raw`

## Usage Example

```python
from pathlib import Path

from level_5 import find_metadata_dir, get_writable_metadata_dir, load_combo_metadata

meta_dir = find_metadata_dir("csiro-metadata")
if meta_dir:
    data = load_combo_metadata(meta_dir, "data_manipulation/metadata.json")

writable = get_writable_metadata_dir("my-metadata")
```
