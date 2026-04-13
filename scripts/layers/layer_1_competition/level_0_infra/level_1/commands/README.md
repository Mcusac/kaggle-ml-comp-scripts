---
generated: 2026-04-08
---

# infra/level_1/handlers/commands — CLI command factories

**Import:** Used via `layers.layer_1_competition.level_0_infra.level_1.handlers.get_command_handlers`, not typically imported directly.

## Purpose

Implements `make_handler(builder) -> Callable[[Namespace], None]` factories for each `run.py` subcommand (train, test, grid_search, cross_validate, train_test, ensemble, export_model).

## Contents

| Module | Description |
|--------|-------------|
| `cross_validate`, `ensemble`, `export_model`, `grid_search`, `test`, `train`, `train_test` | Per-command handler factories |

## Public API

This package’s `__init__.py` exports an empty `__all__`; public commands are wired through `command_handlers.get_command_handlers`.

## Dependencies

- **`layers.layer_0_core.level_0`** … **`level_9`**: core pipelines, workflows, and utilities as required per command
- **`layers.layer_1_competition.level_0_infra.level_0`**: `create_pipeline_kwargs` where needed
- **`layers.layer_1_competition.level_0_infra.level_1.handlers.handler_context`**: shared handler setup

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_1 import get_command_handlers

handlers = get_command_handlers(builder)
handlers["train"](args)
```
