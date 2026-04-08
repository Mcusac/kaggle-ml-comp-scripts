## Purpose

Tiny helpers to build shared pipeline kwargs and training-config dictionaries for contest workflows.

## Contents

| Module | Description |
|--------|-------------|
| `pipeline_kwargs` | Builds common kwargs for pipeline entrypoints |
| `contest_training_config` | Builds a training-config dict compatible with core training helpers |

## Public API

Exported from `layers.layer_1_competition.level_0_infra.level_0.pipeline`:

- **create_pipeline_kwargs**
- **create_training_config**

## Dependencies

- `layers.layer_0_core.level_0`: `build_training_config`
- Stdlib only (`typing`) for `create_pipeline_kwargs`

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_0.pipeline import create_pipeline_kwargs

kwargs = create_pipeline_kwargs(
    paths=object(),
    data_schema=object(),
    model_type="resnet18",
)
```
