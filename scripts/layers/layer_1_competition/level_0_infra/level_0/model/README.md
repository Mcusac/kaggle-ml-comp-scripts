## Purpose

Small model-related helpers shared across contests (model id mapping, feature catalog registration, and export-output verification hooks).

## Contents

| Module | Description |
|--------|-------------|
| `model_constants` | Model-name mapping and pretrained-weights path helpers |
| `feature_catalog` | Registers contest-wide feature definitions into the core feature registry |
| `embeddings` | Framework placeholder functions for embedding/feature loading (contest must implement) |
| `verify_export_output` | Validates exported model directory contents |

## Public API

Exported from `layers.layer_1_competition.level_0_infra.level_0.model`:

- **MODEL_ID_MAP**
- **get_model_id**
- **get_model_image_size**
- **get_model_name_from_pretrained**
- **get_pretrained_weights_path**
- **load_embedding_data**
- **load_structured_features**
- **register_model_id_map**
- **register_features**
- **verify_export_output**

## Dependencies

- `layers.layer_0_core.level_0`: logging and export verification
- `layers.layer_0_core.level_1`: model id helpers and feature registries
- `numpy`

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_0.model import (
    get_model_id,
    get_pretrained_weights_path,
    register_features,
    register_model_id_map,
)

register_model_id_map()
register_features()
_ = get_model_id("resnet18")
_ = get_pretrained_weights_path("resnet18")
```
