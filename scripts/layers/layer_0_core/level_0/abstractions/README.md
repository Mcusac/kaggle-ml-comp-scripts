# Abstractions

Protocol definitions for contest-agnostic orchestration.

## Purpose

Protocols that define interfaces implemented by the contest layer. Orchestration uses these via dependency injection without importing contest-specific code.

## Contents

- `handler_context_builder.py` – HandlerContextBuilder protocol
- `grid_search_context.py` – GridSearchContext protocol

## Public API

- `HandlerContextBuilder` – Protocol for building handler context (detect_contest, get_config, get_paths, get_data_schema, load_contest_data)
- `GridSearchContext` – Protocol for grid search pipeline context (get_paths, get_config, get_metric_calculator, get_metadata_handler, get_feature_cache_loader, get_parameter_grid_fn)

## Dependencies

stdlib only (typing, argparse).

## Usage Example

```python
from level_0 import HandlerContextBuilder, GridSearchContext

def run_with_context(builder: HandlerContextBuilder):
    contest = builder.detect_contest(args)
    config = builder.get_config(contest, args)
```
