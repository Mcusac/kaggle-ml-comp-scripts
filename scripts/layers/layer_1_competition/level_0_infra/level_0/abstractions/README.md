# infra/level_0/abstractions — Contest protocols

**On disk:** `…/level_0_infra/level_0/abstractions/`. **Import:** `layers.layer_1_competition.level_0_infra.level_0` (protocols are part of the `infra level_0` barrel).

## Purpose

Protocol definitions for contest pipelines (`ContestPipelineProtocol`, `ContestInputValidator`, `ContestMetric`). Contest code under `level_1_impl/level_<name>/` implements these; import paths use `layers.layer_1_competition.level_1_impl.<contest>` per project rules.

## Contents

| Module | Description |
|--------|-------------|
| `contest_abstractions` | ContestPipelineProtocol, ContestInputValidator, ContestMetric |

## Public API

- **ContestPipelineProtocol** — Protocol for train_pipeline, submit_pipeline, tune_pipeline
- **ContestInputValidator** — Protocol for validate_inputs
- **ContestMetric** — Protocol for compute(y_pred, y_true, config, **kwargs)

## Dependencies

- None (stdlib only: pathlib, typing)

## Usage Example

```python
from pathlib import Path
from typing import Optional

from layers.layer_1_competition.level_0_infra.level_0 import ContestPipelineProtocol

class MyContestPipeline(ContestPipelineProtocol):
    def train_pipeline(self, data_root: str, **kwargs) -> Optional[Path]:
        raise NotImplementedError

    def submit_pipeline(self, data_root: str, strategy: str, **kwargs) -> Path:
        raise NotImplementedError

    def tune_pipeline(self, data_root: str, **kwargs) -> Optional[Path]:
        raise NotImplementedError
```
# infra/level_0/contest — Contest abstractions

**On disk:** `…/level_0_infra/level_0/contest/`. **Import:** `layers.layer_1_competition.level_0_infra.level_0` (types are re-exported from the `infra level_0` package root).

## Purpose

Abstract base classes that define the contest contract. Each contest implementation (e.g., CSIRO, CAFA, RNA3D) provides concrete implementations of these interfaces.

## Contents

| Module | Description |
|--------|-------------|
| `config` | ContestConfig — target weights, order, primary/derived targets, constraint matrix |
| `data_schema` | ContestDataSchema — sample ID column, target columns, validation |
| `paths` | ContestPaths — Kaggle/local paths, data root, output dir |
| `post_processor` | ContestPostProcessor, ClipRangePostProcessor |
| `ontology` | ContestOntologySystem — ontology codes, names, config |
| `hierarchy` | ContestHierarchy — ancestors, descendants, label propagation |
| `path_config` | ContestPathConfig — dataclass for path configuration |

## Public API

- **ContestConfig** — Abstract config: target_weights, target_order, primary_targets, derived_targets, compute_derived_targets, constraint_matrix
- **ContestDataSchema** — Abstract schema: sample_id_column, target_columns, feature_columns, validate_sample_id, get_sample_weights
- **ContestPaths** — Abstract paths: kaggle_dataset_name, local_data_root, get_data_root, get_output_dir
- **ContestPostProcessor** — Abstract post-processor: apply, enforce_constraints, clip_values
- **ClipRangePostProcessor** — Concrete post-processor that clips to [min, max]
- **ContestOntologySystem** — Abstract ontology: ontology_codes, ontology_names, get_ontology_config
- **ContestHierarchy** — Abstract hierarchy: get_ancestors, get_descendants, get_parents, get_children, propagate_labels
- **ContestPathConfig** — Dataclass for path configuration (data_root, output_dir, cache_dir, etc.)

## Dependencies

- `layers.layer_0_core.level_0`: `is_kaggle`
- `layers.layer_0_core.level_5`: `find_project_input_root`

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_0 import ContestPaths

# Contest implementations extend these base classes
class MyContestPaths(ContestPaths):
    @property
    def kaggle_dataset_name(self) -> str:
        return "my-contest-dataset"

    @property
    def kaggle_competition_name(self):
        return "my-contest"

    @property
    def local_data_path(self) -> str:
        return "data/my-contest"
```
