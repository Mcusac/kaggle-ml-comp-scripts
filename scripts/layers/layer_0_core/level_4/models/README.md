# level_4.models

## Purpose

Factory for creating vision models. Supports DINOv2 (HuggingFace) and timm-based architectures (EfficientNet, ResNet, ViT, etc.).

## Contents

| Module | Description |
|--------|-------------|
| vision_model_factory | create_vision_model |

## Public API

| Export | Description |
|--------|-------------|
| create_vision_model | Factory for vision models (DINOv2, timm) |

## Dependencies

- **level_0** — get_logger
- **level_1** — BaseVisionModel
- **level_2** — DINOv2Model
- **level_3** — TimmModel

## Usage Example

```python
from level_4 import create_vision_model

model = create_vision_model("efficientnet_b0", num_classes=5)
model = create_vision_model("dinov2-base", num_classes=5, input_size=(518, 518))
```
