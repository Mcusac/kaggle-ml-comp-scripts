# infra/level_2/registry — Contest CLI handler module paths

**On disk:** `…/level_0_infra/level_2/registry/`.  
**Import:** `layers.layer_1_competition.level_0_infra.level_2` (barrel).

## Purpose

Associate each registered contest with a dotted Python module path for its CLI command handlers, stored on the existing `ContestRegistry` entry (`cli_handlers_module`). Resolution uses `importlib.import_module` without importing contest code until handlers are needed.

## Contents

| Module | Description |
|--------|-------------|
| `cli_handlers.py` | `register_cli_handlers_module`, `list_contests_with_cli_handlers`, `get_cli_handlers_module`. |

## Public API

- **register_cli_handlers_module** — Set `entry["cli_handlers_module"]` after the contest is registered.
- **list_contests_with_cli_handlers** — Sorted contest keys with a non-empty handlers path.
- **get_cli_handlers_module** — Import and return the handlers module; raises if missing or contest unknown.

## Dependencies

- **`layers.layer_1_competition.level_0_infra.level_1`:** `ContestRegistry`.

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_2 import (
    get_cli_handlers_module,
    register_cli_handlers_module,
)

register_cli_handlers_module(
    "csiro",
    "layers.layer_1_competition.level_1_impl.level_csiro.level_7.handlers",
)
handlers = get_cli_handlers_module("csiro")
```
