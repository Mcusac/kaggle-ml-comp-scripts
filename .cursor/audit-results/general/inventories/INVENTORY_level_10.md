---
generated: 2026-04-08
audit_scope: general
level_name: level_10
pass_number: 1
run_id: general-stack-orchestrator-2026-04-08
artifact_kind: inventory
audit_profile: full
precheck_report_path: c:\Users\mdc0431\OneDrive - UNT System\Documents\Kaggle\code\input\kaggle-ml-comp-scripts\.cursor\audit-results\general\summaries\precheck_level_10_2026-04-08.md
---

# INVENTORY: level_10

## 1. Package & File Tree

```
level_10/
  README.md
  __init__.py
  end_to_end_grid_search/
    README.md
    __init__.py
    pipeline.py
```

## 2. Per-File Details

```
FILE: level_10/__init__.py
  Module docstring: Level 10: Train-then-predict workflow.
  Classes: (none)
  Functions: (none)
  Imports:
    - from .end_to_end_grid_search import EndToEndGridSearch, hyperparameter_grid_search_pipeline [internal]
  Line count: 6
  __all__: ["EndToEndGridSearch", "hyperparameter_grid_search_pipeline"]
```

```
FILE: level_10/end_to_end_grid_search/__init__.py
  Module docstring: End-to-end hyperparameter grid search. Requires contest_context from contest layer.
  Classes: (none)
  Functions: (none)
  Imports:
    - from .pipeline import EndToEndGridSearch, hyperparameter_grid_search_pipeline [internal]
  Line count: 9
  __all__: ["EndToEndGridSearch", "hyperparameter_grid_search_pipeline"]
```

```
FILE: level_10/end_to_end_grid_search/pipeline.py
  Module docstring: End-to-end hyperparameter grid search implementation.
  Classes:
    - EndToEndGridSearch
        Methods:
          __init__(self, config: Union[Any, Dict[str, Any]], search_type: str = SEARCH_TYPE_THOROUGH, train_pipeline_fn: Optional[Any] = None, **kwargs)
          _create_variant_key(self, variant: tuple) -> Tuple
          _create_variant_key_from_result(self, result: Dict[str, Any]) -> Optional[Tuple]
          _run_variant(self, variant: tuple, variant_index: int, **kwargs) -> Dict[str, Any]
  Functions:
    - hyperparameter_grid_search_pipeline(contest_context: Any, train_pipeline_fn: Optional[Any] = None, config: Optional[Union[Any, Dict[str, Any]]] = None, search_type: str = SEARCH_TYPE_THOROUGH, **kwargs) -> None
  Imports:
    - from typing import Any, Dict, Optional, Tuple, Union [stdlib]
    - from layers.layer_0_core.level_0 import (BEST_HYPERPARAMETERS_FILE, ConfigValidationError, RESULTS_FILE_GRIDSEARCH, SEARCH_TYPE_THOROUGH, get_logger) [internal]
    - from layers.layer_0_core.level_1 import get_transformer_hyperparameter_grid [internal]
    - from layers.layer_0_core.level_4 import save_json [internal]
    - from layers.layer_0_core.level_7 import HyperparameterGridSearchBase [internal]
    - from layers.layer_0_core.level_8 import create_end_to_end_variant_result, extract_variant_config [internal]
    - from layers.layer_0_core.level_9 import attach_paths_to_config [internal]
  Line count: 152
  __all__: (not defined)
```

## 3. __init__.py Public API Summary

```
INIT: level_10/__init__.py
  Exports: EndToEndGridSearch, hyperparameter_grid_search_pipeline
  Re-exports from: level_10.end_to_end_grid_search
```

```
INIT: level_10/end_to_end_grid_search/__init__.py
  Exports: EndToEndGridSearch, hyperparameter_grid_search_pipeline
  Re-exports from: level_10.end_to_end_grid_search.pipeline
```

## 4. Import Dependency Map

```
INTERNAL IMPORTS SUMMARY:
  From layers.layer_0_core.level_0: BEST_HYPERPARAMETERS_FILE, ConfigValidationError, RESULTS_FILE_GRIDSEARCH, SEARCH_TYPE_THOROUGH, get_logger
  From layers.layer_0_core.level_1: get_transformer_hyperparameter_grid
  From layers.layer_0_core.level_4: save_json
  From layers.layer_0_core.level_7: HyperparameterGridSearchBase
  From layers.layer_0_core.level_8: create_end_to_end_variant_result, extract_variant_config
  From layers.layer_0_core.level_9: attach_paths_to_config
  From same level (level_10): relative imports in __init__.py files and end_to_end_grid_search package
  From level_11 or higher: (none observed)
```

## 5. FLAGS

```
FLAGS:
  level_10/__init__.py — 6 lines (small); module docstring says "Train-then-predict workflow" while exports are EndToEndGridSearch / hyperparameter_grid_search_pipeline (textual mismatch vs exports)
  level_10/end_to_end_grid_search/pipeline.py — 152 lines (single logic module for level)
  Keywords (deprecated, legacy, compat, backwards, TODO: remove, shim): (none found)
  Duplicate public symbols across files: (none; single definition sites for exported names)
```

## 6. Static scan summary (precheck)

- Source: `precheck_level_10_2026-04-08.md` under general summaries.
- `precheck_status`: skipped_machine_script (`ModuleNotFoundError: No module named 'torchvision'`).
- Machine Phase 7 reconciliation / devtools precheck stack did not run in the environment that produced the precheck artifact.
