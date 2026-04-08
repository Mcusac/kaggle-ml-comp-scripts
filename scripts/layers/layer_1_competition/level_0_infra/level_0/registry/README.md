## Purpose

Small string-keyed registry primitives used by competition infra and contests.

## Contents

| Module | Description |
|--------|-------------|
| `__init__` | Re-exports `NamedRegistry` and `build_unknown_key_error` from the core level |

## Public API

Exported from `layers.layer_1_competition.level_0_infra.level_0.registry`:

- **NamedRegistry**
- **build_unknown_key_error**

## Dependencies

- `layers.layer_0_core.level_0`: registry primitives

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_0.registry import NamedRegistry

reg: NamedRegistry[int] = NamedRegistry(name="example")
reg.register("x", 1)
```
