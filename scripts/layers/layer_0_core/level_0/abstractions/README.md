# Abstractions

Protocol and base types for contest-agnostic orchestration.

## Purpose

Abstract base classes, registries, and typing.Protocol definitions used for dependency injection. Higher layers implement these interfaces without `level_0` importing contest code.

## Contents

- `ensembling_method.py` – `EnsemblingMethod` ABC for prediction fusion
- `grid_search_context.py` – `GridSearchContext` protocol for grid-search pipelines
- `handler_context_builder.py` – `HandlerContextBuilder` protocol for CLI/handler wiring
- `metric.py` – `Metric` ABC for scoring callables
- `model_registry.py` – `ModelRegistry` classmethods for model factory registration
- `named_registry.py` – `NamedRegistry`, `build_unknown_key_error`
- `pipeline_result.py` – `PipelineResult` frozen dataclass with `ok` / `fail` factories

## Public API

- `EnsemblingMethod` – Combine arrays of predictions with optional weights
- `GridSearchContext` – Paths, config, metric calculator, metadata, cache loader, parameter grid hook
- `HandlerContextBuilder` – Detect contest, load config/paths/schema/data for a contest name
- `Metric` – Named metric with `calculate` / `__call__` on `y_true` / `y_pred`
- `ModelRegistry` – `register` / `create` / `is_registered` for model type strings
- `NamedRegistry` – Generic keyed registry with `register` decorator, `get` / `require`
- `build_unknown_key_error` – Format a consistent unknown-key message for registries
- `PipelineResult` – Success/failure value object with stage, error, artifacts, metadata

## Dependencies

stdlib only (abc, argparse, dataclasses, typing).

## Usage Example

```python
from level_0 import HandlerContextBuilder, ModelRegistry

def run_with_context(builder: HandlerContextBuilder):
    contest = builder.detect_contest(args)
    config = builder.get_config(contest, args)
```
