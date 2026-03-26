# grid_search

## Purpose

Grid search result persistence, checkpoint cleanup, result analysis, and variant tracking. Orchestration (e.g. run_variant_cleanup) is provided by higher levels; this package exposes the helpers only.

## Contents

- **checkpoint_cleanup.py**: cleanup_grid_search_checkpoints_retroactive, cleanup_checkpoints
- **result_analysis.py**: load_raw_results, extract_top_results, extract_parameter_ranges, analyze_results_for_focused_grid, get_focused_parameter_grid
- **results_persistence.py**: load_results, save_results, load_checkpoint, save_checkpoint
- **variant_tracking.py**: load_completed_variants_helper, get_next_variant_index, save_variant_result_helper

## Public API

- `cleanup_grid_search_checkpoints_retroactive(model_base_dir, results_file, keep_top_n=20)` — Delete non-top-N variant dirs
- `cleanup_checkpoints(grid_search_dir, keep_top_n=5, results=None)` — Delete non-top-N from results list
- `load_raw_results(results_file)` — Load results JSON as list
- `extract_top_results(results, top_n=10, metric_key='cv_score')` — Top N by metric
- `extract_parameter_ranges(top_results, range_expansion_factor=1.5, min_values_per_param=2)` — Focused param ranges
- `analyze_results_for_focused_grid(results_file, ...)` — Full analysis pipeline
- `load_results(results_file)` — (results, best_score, best_variant, completed_variants)
- `save_results(results_file, grid_search_type, total_variants, ...)` — Persist full result set
- `load_checkpoint(checkpoint_dir, param_grid=None)` — Load latest checkpoint
- `save_checkpoint(checkpoint_dir, ...)` — Write timestamped checkpoint
- `load_completed_variants_helper(results_file, keep_top_n, create_variant_key_from_result_fn)` — Load completed/skipped
- `get_next_variant_index(all_results)` — Next sequential index
- `save_variant_result_helper(result, results_file)` — Incremental append

## Dependencies

- level_0: extract_results_list, get_logger, merge_focused_ranges_into_base_grid
- level_1: get_transformer_hyperparameter_grid (result analysis / focused grid only)
- level_4: load_json, save_json

## Usage Example

```python
from level_5 import (
    load_results,
    save_results,
    load_checkpoint,
    save_checkpoint,
    load_raw_results,
    extract_top_results,
    analyze_results_for_focused_grid,
    cleanup_grid_search_checkpoints_retroactive,
)
from pathlib import Path

results, best_score, best_variant, completed = load_results(Path("results.json"))
ranges = analyze_results_for_focused_grid("results.json", top_n=10)
deleted, freed = cleanup_grid_search_checkpoints_retroactive("models", "results.json", keep_top_n=20)
```
