# file_io

## Purpose

Merge utilities for combining JSON/list data from input (read-only) and working (writable) directories.

## Contents

- **merge.py**: merge_list_by_key_add_only, merge_list_by_key_working_replaces, merge_json_from_input_and_working

## Public API

- `merge_list_by_key_add_only(input_items, working_items, key_fn)` — Add working items whose key not in input
- `merge_list_by_key_working_replaces(input_items, working_items, key_fn)` — Working replaces input for same key
- `merge_json_from_input_and_working(input_path, working_path, merge_fn, expected_type=list, file_type="JSON")` — Load both, merge with merge_fn

## Dependencies

- level_4: load_json

## Usage Example

```python
from layers.layer_0_core.level_5 import merge_json_from_input_and_working, merge_list_by_key_add_only
from pathlib import Path

key_fn = lambda x: x.get("variant_id")
merged = merge_json_from_input_and_working(
    Path("/kaggle/input/results.json"),
    Path("/kaggle/working/results.json"),
    lambda i, w: merge_list_by_key_add_only(i, w, key_fn),
)
```
