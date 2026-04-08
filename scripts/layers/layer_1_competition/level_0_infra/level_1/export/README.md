---
generated: 2026-04-08
---

# infra/level_1/export — Export model pipeline

**On disk:** `…/level_0_infra/level_1/export/`. **Import:** `layers.layer_1_competition.level_0_infra.level_1` (preferred) or `…level_1.export` for submodule cycle breaks.

## Purpose

Orchestrates model export for submission: resolves sources (just-trained dir, best-variant file, or results CSV), builds metadata, and writes the export tree.

## Contents

| Module | Description |
|--------|-------------|
| `export_model_pipeline` | Top-level export orchestration |
| `feature_filename` | Feature artifact name resolution from config |
| `metadata_builders` | Regression/end-to-end metadata dicts |
| `source_handlers` | `handle_just_trained_model`, `handle_best_variant_file`, `handle_results_file` |

## Public API

- **export_model_pipeline** — main entry; takes `contest_context` and optional `model_dir`, `results_file`, `variant_id`, `best_variant_file`, `export_dir`
- **prepare_regression_model_metadata_dict**, **handle_*** — supporting symbols re-exported on `export/__init__.py`

`export_model_pipeline` imports `source_handlers` by submodule path intentionally to avoid an import cycle with `export/__init__.py`.

## Dependencies

- **`layers.layer_0_core.level_0`**, **`level_4`**, **`level_5`**: directories, logging, JSON/CSV, trained-model discovery
- **`layers.layer_1_competition.level_0_infra.level_0`**: model naming helpers where needed

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_1 import build_contest_context, export_model_pipeline

ctx = build_contest_context("csiro")
path = export_model_pipeline(ctx, model_dir="output/models/run_001")
```
