# infra/level_1/export — Export model pipeline

**On disk:** `…/level_0_infra/level_1/export/`. **Import:** `layers.layer_1_competition.level_0_infra.level_1`.

## Purpose

Orchestrates model export for submission. `export_handlers` is the stable compatibility surface, now split internally into focused modules:
- `metadata_builders` (metadata assembly and score extraction)
- `source_handlers` (source-file/model-dir resolution flows)

## Contents

| Module | Description |
|--------|-------------|
| `export_model_pipeline` | export_model_pipeline function |
| `export_handlers` | Compatibility exports for existing imports |
| `metadata_builders` | Metadata-building helpers for regression/end-to-end models |
| `source_handlers` | Handler flows for best-variant/results/auto-detect sources |

## Public API

- **export_model_pipeline** — Export trained model. Accepts ContestContext and optional model_dir, results_file, variant_id, best_variant_file, export_dir. Returns export path string.

## Dependencies

- **level_0:** ensure_dir, get_logger
- **layers.layer_1_competition.level_0_infra.level_1.export.export_handlers:** handle_auto_detect, handle_best_variant_file, handle_just_trained_model, handle_results_file

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_1 import build_contest_context, export_model_pipeline

ctx = build_contest_context("csiro")
path = export_model_pipeline(ctx, model_dir="output/models/run_001")
```
