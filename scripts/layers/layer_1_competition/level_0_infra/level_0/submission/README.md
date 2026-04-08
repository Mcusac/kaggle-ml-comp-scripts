## Purpose

Common validation helpers for submission strategy selection.

## Contents

| Module | Description |
|--------|-------------|
| `strategy_validation` | Validates that a chosen submission strategy is compatible with the number of selected models |

## Public API

Exported from `layers.layer_1_competition.level_0_infra.level_0.submission`:

- **validate_strategy_models**

## Dependencies

- Stdlib only (`typing`)

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_0.submission import validate_strategy_models

validate_strategy_models("ensemble", ["m1", "m2"])
```
