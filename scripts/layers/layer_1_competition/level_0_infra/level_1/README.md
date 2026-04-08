---
generated: 2026-04-08
---

# infra/level_1 — Feature extraction, export, handlers, paths

**On disk:** `scripts/layers/layer_1_competition/level_0_infra/level_1/`.  
**Import:** `layers.layer_1_competition.level_0_infra.level_1`.

## Purpose

Contest-agnostic building blocks on top of infra `level_0`: registry and paths, shared contest CLI/data loading, feature-extraction factory, export orchestration, grid-search base/context, `run.py` command handlers, notebook helpers, and small pipeline shells.

## Contents

| Sub-package | Description |
|-------------|-------------|
| `contest/` | Argparse, context, CSV IO, splits, data-loading facade, validate-first shells (from core pipelines) |
| `export/` | `export_model_pipeline` and source/metadata helpers |
| `features/` | Vision feature extraction factory |
| `grid_search/` | Contest grid-search base and context types |
| `handlers/` | `get_command_handlers` and per-command factories |
| `notebook/` | Notebook CLI dispatch and streaming |
| `paths/` | Contest path resolution and Kaggle heuristics |
| `pipelines/` | `ValidateTrainSubmitPipelineResultShell` |
| `registry/` | Contest registration and detection |

## Public API

All names in `level_1/__init__.py` `__all__` (union of child packages), including for example: `get_command_handlers`, `export_model_pipeline`, `create_feature_extraction_model`, `build_contest_context`, `ContestRegistry`, `get_contest`, path helpers, grid-search types, notebook helpers, pipeline shells (`ValidateTrainSubmitPipelineResultShell`, `TwoStageValidateFirstPipelineResultShell`, …), and contest CLI symbols re-exported from `contest`.

## Dependencies

- **`layers.layer_0_core`** (`level_0`–`level_9`): core logging, IO, pipelines, workflows, torch helpers as used by each module
- **`layers.layer_1_competition.level_0_infra.level_0`**: `ContestPaths`, `PipelineResult`, `create_pipeline_kwargs`, pretrained path helpers, and related contracts

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_1 import (
    build_contest_context,
    export_model_pipeline,
    get_command_handlers,
)

ctx = build_contest_context("csiro")
path = export_model_pipeline(ctx, model_dir="output/models/run_001")
handlers = get_command_handlers(builder)
```
