# infra/level_1/handlers — CLI command handlers

**On disk:** `…/level_0_infra/level_1/handlers/`. **Import:** `layers.layer_1_competition.level_0_infra.level_1`.

## Purpose

Framework command handlers for train, test, train-test, grid search, cross-validation, ensemble, and export. Uses injected HandlerContextBuilder to avoid direct contest imports.

## Contents

| Module | Description |
|--------|-------------|
| `command_handlers` | get_command_handlers, _setup_handler_context, _make_handlers |

## Public API

- **get_command_handlers** — Returns dict mapping Command enum values to handler callables. Accepts HandlerContextBuilder.

## Dependencies

- **level_0:** Command, get_arg, parse_comma_separated, ensure_dir, get_logger
- **level_2:** simple_average
- **level_5:** ExportPipeline
- **level_6:** PredictPipeline
- **level_8:** TrainPipeline
- **level_9:** CrossValidateWorkflow, HyperparameterGridSearch, TrainPredictWorkflow
- **layers.layer_1_competition.level_0_infra.level_0:** create_pipeline_kwargs

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_1 import get_command_handlers
from run_helpers import get_handler_context_builder

builder = get_handler_context_builder("csiro")
handlers = get_command_handlers(builder)
handlers["train"](args)
```
