# level_4.features

## Purpose

SigLIP-based feature extraction: batch extraction from DataFrames and adapter for FeatureExtractor interface (tensor in, tensor out).

## Contents

| Module | Description |
|--------|-------------|
| compute_siglip_embeddings | Extract SigLIP embeddings from DataFrame |
| siglip_adapter | SigLIPFeatureExtractorAdapter for FeatureExtractor interface |

## Public API

| Export | Description |
|--------|-------------|
| compute_siglip_embeddings | Extract SigLIP embeddings from DataFrame |
| SigLIPFeatureExtractorAdapter | Adapter for SigLIP in FeatureExtractor interface |

## Dependencies

- **level_0** — get_torch
- **level_3** — SigLIPExtractor

## Usage Example

```python
from level_4 import compute_siglip_embeddings, SigLIPFeatureExtractorAdapter

embeddings = compute_siglip_embeddings(
    model_path="/path/to/siglip",
    df=df,
    image_path_col="image_path",
)
```
