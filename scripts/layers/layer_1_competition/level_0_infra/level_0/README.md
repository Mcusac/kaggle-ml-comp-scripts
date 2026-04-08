## Purpose

Base contracts and lightweight utilities shared by contest implementations (contest config/schema/paths/post-processing interfaces, CLI parser wiring helpers, artifact key conventions, and a few small model/path helpers).

## Contents

| Subpackage | What it contains |
|-----------|-------------------|
| `abstractions/` | Contest-facing Protocols (`ContestPipelineProtocol`, `ContestInputValidator`, `ContestMetric`) plus `PipelineResult` re-export |
| `artifacts/` | Artifact/metadata key conventions and merge helpers for `PipelineResult` capture |
| `cli/` | CLI parser-builder helpers (adds contest subcommands and shared flags) |
| `contest/` | Abstract base classes defining the contest contract (config, data schema, paths, hierarchy/ontology, post-processing) |
| `model/` | Small model/feature catalog helpers and export verification |
| `paths/` | Small path helpers (contest output dir helpers, metadata fallbacks) |
| `pipeline/` | Creation helpers for common pipeline kwargs / training-config dictionaries |
| `registry/` | String-keyed registry base types (re-exported from core) |
| `submission/` | Submission strategy validation helpers |

## Public API

Exported from `layers.layer_1_competition.level_0_infra.level_0` (root `__init__.py`):

- `ContestPipelineProtocol`, `ContestInputValidator`, `ContestMetric`, `ContestRunPathsProtocol`, `PipelineResult`
- `ArtifactKeys`, `artifacts_merge`, `metadata_merge`, `capture_*_paths`
- `add_grid_search_parsers`, `add_training_parsers`, `add_ensemble_parsers`, `add_submission_parsers`
- `ContestConfig`, `ContestDataSchema`, `ContestPaths`, `ContestPostProcessor`, `ClipRangePostProcessor`, `ContestOntologySystem`, `ContestHierarchy`, `ContestPathConfig`
- `MODEL_ID_MAP`, `get_model_id`, `get_model_image_size`, `get_model_name_from_pretrained`, `get_pretrained_weights_path`, `load_embedding_data`, `load_structured_features`, `register_model_id_map`, `register_features`, `verify_export_output`
- `contest_models_dir`, `load_feature_filename_from_gridsearch`
- `create_pipeline_kwargs`, `create_training_config`
- `NamedRegistry`, `build_unknown_key_error`
- `validate_strategy_models`

## Dependencies

- `layers.layer_0_core.level_0`: logging, runtime helpers, registry primitives, `PipelineResult`
- `layers.layer_0_core.level_1`: model id helpers and feature registry globals
- `layers.layer_0_core.level_5`: `find_project_input_root` (via the `level_5` public API)

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_0 import (
    ContestPaths,
    contest_models_dir,
    get_pretrained_weights_path,
    register_model_id_map,
)

def resolve_run_models_dir(*, paths: ContestPaths, contest_slug: str) -> str:
    register_model_id_map()
    models_dir = contest_models_dir(paths, contest_slug)
    _ = get_pretrained_weights_path("resnet18")
    return str(models_dir)
```
