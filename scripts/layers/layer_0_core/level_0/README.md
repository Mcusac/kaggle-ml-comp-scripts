# Level 0: Core Utilities

Foundational utilities with no dependencies on other package layers. Imported by level_1 and all higher layers.

## Purpose

CLI argument parsing and dispatch, exception hierarchy, base config schemas, path helpers, grid search combinatorics and result selection, embedding alignment, prediction guards, protein feature constants, scoring utilities, training loop primitives, environment detection, logging, and vision transform/image I/O utilities.

## Contents

| Subpackage | Responsibility |
|------------|----------------|
| `abstractions` | ABCs and protocols: `EnsemblingMethod`, `Metric`, `ModelRegistry`, `NamedRegistry`, `GridSearchContext`, `HandlerContextBuilder`, `PipelineResult`, `build_unknown_key_error` |
| `cli` | Argument parsing helpers, argument group builders, `Command` enum, `dispatch_command` |
| `config` | `BaseConfig`, `TrainingSchema`, `EvaluationSchema`, `PathConfig`, `CompositeConfig`, `RuntimeConfig`, `PipelineConfig`, `TrainingCadenceConfig`, `TrainingMode`, `DataSplit`, `get_config_value` |
| `embeddings` | `align_embeddings`, `find_common_ids`, `normalize_embedding_type`, `resolve_embedding_base_path` |
| `errors` | Full exception hierarchy: `ConfigError`, `DataError`, `ModelError`, `PipelineError`, runtime errors |
| `grid_search` | Combinatorics, parameter grid building, result builders, result selection, constants |
| `ontology` | `parse_obo_file` (OBO format parsing) |
| `paths` | `ensure_dir`, `normalize_path`, `get_file_size_mb`, `ensure_file_dir`, fold checkpoint paths |
| `prediction_guards` | Array/list validation for predictions, `verify_export_files` |
| `protein_features` | Amino acid physicochemical constants, `extract_kmer_frequencies` |
| `runtime` | `is_kaggle`, logging, `get_torch`, `run_command_stream`, `BaseCommandBuilder`, `ExecutionResult`, `DerivedCachePaths`, typed dicts |
| `scoring` | `calculate_percentile_weights`, `combine_predictions_loop`, `combine_predictions_vectorized`, `combine_predictions_weighted_average`, `fit_stacking_weights_from_scores` |
| `training` | `build_training_config`, `extract_batch_data`, `create_history_entry`, `get_scheduler_mode`, `step_scheduler` |
| `vision` | Image I/O (`load_image_pil`, `load_image_rgb`, `split_image`), transform utilities, noise reduction, `TransformMode` |

## Public API

All names exported from each subpackage's `__init__.py`. See each subpackage README for details.

## Dependencies

stdlib only. Optional: torch, torchvision, scipy. No imports from level_1 or higher.

## Usage Example

```python
from level_0 import is_kaggle, setup_logging, dispatch_command
from level_0 import RuntimeConfig, DataSplit, calculate_percentile_weights
from level_0 import load_image_pil, build_minimal_val_transform
```
