## Purpose

Small, contest-agnostic path helpers used by competition orchestration (output directory conventions and metadata-based fallbacks).

## Contents

| Module | Description |
|--------|-------------|
| `contest_output` | Output directory helpers (e.g. `<output>/models/<contest>`) |
| `metadata_fallback` | Helpers for extracting missing metadata fields from grid-search results |

## Public API

Exported from `layers.layer_1_competition.level_0_infra.level_0.paths`:

- **contest_models_dir**
- **load_feature_filename_from_gridsearch**

## Dependencies

- `layers.layer_0_core.level_0`: logging
- `layers.layer_1_competition.level_0_infra.level_0.contest`: `ContestPaths`

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_0 import ContestPaths
from layers.layer_1_competition.level_0_infra.level_0.paths import contest_models_dir

def resolve_models_dir(paths: ContestPaths) -> str:
    return str(contest_models_dir(paths, contest_slug="csiro"))
```
