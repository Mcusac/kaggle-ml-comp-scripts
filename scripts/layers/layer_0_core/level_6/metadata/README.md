# level_6.metadata

## Purpose

Helpers for reading competition metadata and resolving identifiers from config (e.g. combo id lookup).

## Contents

- `combo_lookup.py` — `find_combo_id_from_config`

## Public API

| Name | Description |
|------|-------------|
| `find_combo_id_from_config` | Return combo id string for a config if present in metadata, else `None` |

## Dependencies

- **level_0**: `get_logger`
- **level_4**: `load_json_raw`
- **level_5**: `find_metadata_dir`

## Usage Example

```python
from layers.layer_0_core.level_6 import find_combo_id_from_config

combo_id = find_combo_id_from_config(config)
```
