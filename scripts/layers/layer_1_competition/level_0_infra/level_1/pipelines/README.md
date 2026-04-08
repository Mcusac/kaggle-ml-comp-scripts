---
generated: 2026-04-08
---

# infra/level_1/pipelines — Competition pipeline result shells

**Import:** `layers.layer_1_competition.level_0_infra.level_1` or `…level_1.pipelines`.

## Purpose

Supplies a `PipelineResult`-oriented shell used for validate-then-train-submit style flows (`ValidateTrainSubmitPipelineResultShell`).

## Contents

| Module | Description |
|--------|-------------|
| `validate_train_submit` | Shell wrapping train/submit stages with `PipelineResult` semantics |

## Public API

- **ValidateTrainSubmitPipelineResultShell** — callable shell with a `run()` producing `PipelineResult` (from infra level_0).

## Dependencies

- **`layers.layer_1_competition.level_0_infra.level_0`**: `PipelineResult`

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_1 import ValidateTrainSubmitPipelineResultShell

# Construct with contest-specific callables and run when wiring a composite pipeline.
```
