# infra/level_1/features — Feature extraction model creation

**On disk:** `…/level_0_infra/level_1/features/`. **Import:** `layers.layer_1_competition.level_0_infra.level_1`.

## Purpose

Creates feature extraction models (SigLIP, DINOv2, timm) and validates feature extraction trainer inputs. Supports optional pretrained weights resolver for SigLIP.

## Contents

| Module | Description |
|--------|-------------|
| `feature_extractor_factory` | create_feature_extraction_model, set_pretrained_weights_resolver |
| `validate_feature_extraction_inputs` | validate_feature_extraction_inputs (delegates to level_1) |

## Public API

- **create_feature_extraction_model** — Create SigLIP, DINOv2, or timm model. Handles pretrained weights via resolver or infra level_0.get_pretrained_weights_path.
- **set_pretrained_weights_resolver** — Set optional callable for SigLIP weights path resolution.
- **validate_feature_extraction_inputs** — Validate config and device for feature extraction trainer.

## Dependencies

- **level_0:** get_logger, get_torch
- **level_1:** validate_feature_extraction_trainer_inputs
- **level_3:** SigLIPExtractor
- **level_4:** create_vision_model, SigLIPFeatureExtractorAdapter
- **layers.layer_1_competition.level_0_infra.level_0:** get_pretrained_weights_path

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_1 import create_feature_extraction_model, set_pretrained_weights_resolver
import torch

# Optional: set custom weights resolver for SigLIP
set_pretrained_weights_resolver(lambda name: "/path/to/weights.pth")

model = create_feature_extraction_model(
    model_name="siglip_so400m_patch14_384",
    num_primary_targets=10,
    device=torch.device("cuda"),
)
```
