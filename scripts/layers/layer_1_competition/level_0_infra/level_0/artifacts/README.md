## Purpose

Standardized keys and tiny helpers for recording artifact and metadata paths in `PipelineResult` objects.

## Contents

| Module | Description |
|--------|-------------|
| `schema` | `ArtifactKeys` plus `capture_*_paths` and merge helpers |

## Public API

Exported from `layers.layer_1_competition.level_0_infra.level_0.artifacts`:

- **ArtifactKeys** — string constants for artifact keys used in `PipelineResult.artifacts`
- **artifacts_merge** — merges multiple artifact-path dicts
- **metadata_merge** — merges multiple metadata dicts
- **capture_config_paths** — helper to build config artifact dict
- **capture_model_paths** — helper to build model artifact dict
- **capture_submission_paths** — helper to build submission artifact dict
- **capture_metrics_paths** — helper to build metrics artifact dict

## Dependencies

- Stdlib only (`typing`)

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_0.artifacts import (
    artifacts_merge,
    capture_model_paths,
)

artifacts = artifacts_merge(
    capture_model_paths(models_dir="output/models", model_checkpoint="output/models/best.ckpt"),
)
```
