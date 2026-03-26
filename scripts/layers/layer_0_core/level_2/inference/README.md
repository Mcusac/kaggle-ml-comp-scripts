# inference

Vision model batch inference.

## Purpose

Provides `VisionPredictor`, which runs a PyTorch vision model over a DataLoader, accumulates predictions, and returns them as a numpy array. Supports mixed-precision inference via AMP.

## Contents

- `vision_predictor.py` — `VisionPredictor`: stateless batch inference runner for vision models

## Public API

- `VisionPredictor` — Runs inference over a DataLoader using a PyTorch model on a specified device; supports AMP

## Dependencies

- **level_0** — `get_logger`, `get_torch`
- **level_1** — `forward_with_amp`

## Usage Example

```python
import torch
from level_2.inference import VisionPredictor

device = torch.device("cuda")
predictor = VisionPredictor(model=model, device=device, use_amp=True)
predictions = predictor.predict(dataloader)
# predictions: np.ndarray of shape (N, num_outputs)
```
