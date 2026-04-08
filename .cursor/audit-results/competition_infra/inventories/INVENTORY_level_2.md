---
generated: 2026-04-08
audit_scope: competition_infra
level_name: level_2
pass_number: 1
run_id: comp_infra_overhaul_2026-04-08
artifact_kind: inventory
audit_profile: full
level_path: c:\Users\mdc0431\OneDrive - UNT System\Documents\Kaggle\code\input\kaggle-ml-comp-scripts\scripts\layers\layer_1_competition\level_0_infra\level_2
precheck_report_path: c:\Users\mdc0431\OneDrive - UNT System\Documents\Kaggle\code\input\kaggle-ml-comp-scripts\.cursor\audit-results\competition_infra\summaries\precheck_level_2_2026-04-08.md
---

#### INVENTORY: `level_2`

#### 1. Package & File Tree

```
level_2/
  README.md
  __init__.py
  feature_extraction/
    README.md
    __init__.py
    feature_extraction_helper.py
    test_extractor.py
  registry/
    README.md
    __init__.py
    cli_handlers.py
```

---

#### 2. Per-File Details

```
FILE: level_2/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from . import feature_extraction                    [internal]
    - from . import registry                             [internal]
    - from .feature_extraction import *                  [internal]
    - from .registry import *                             [internal]
  Line count: 9
  __all__: tuple(list(feature_extraction.__all__) + list(registry.__all__))
```

```
FILE: level_2/feature_extraction/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .feature_extraction_helper import FeatureExtractionHelper  [internal]
    - from .test_extractor import extract_test_features_from_model, find_feature_filename_from_ensemble_metadata  [internal]
  Line count: 13
  __all__: ["FeatureExtractionHelper", "extract_test_features_from_model", "find_feature_filename_from_ensemble_metadata"]
```

```
FILE: level_2/feature_extraction/feature_extraction_helper.py
  Module docstring: Joint feature and target extraction for feature-extraction training.
  Classes:
    - FeatureExtractionHelper
        Methods: __init__(self, feature_extractor: FeatureExtractor, dataset_type: str) -> None
                 extract_all_features(self, loader: Any) -> Tuple[np.ndarray, np.ndarray]
  Functions: (none)
  Imports:
    - from typing import Any, Tuple                       [stdlib]
    - import numpy as np                                  [third_party]
    - from layers.layer_0_core.level_2 import FeatureExtractor  [internal — layer_0_core]
  Line count: 21
  __all__: (none explicit)
```

```
FILE: level_2/feature_extraction/test_extractor.py
  Module docstring: Generic test feature extraction for stacking and ensemble pipelines.
  Classes: (none)
  Functions:
    - extract_test_features_from_model(test_csv_path: Path | str, data_root: str, dataset_type: str, config: Any, data_schema: Any, feature_extraction_model_name: str = "dinov2_base", batch_size: int = _DEFAULT_BATCH_SIZE, num_workers: int = 0) -> np.ndarray
    - find_feature_filename_from_ensemble_metadata(ensemble_configs: list, metadata_key: str = "model_paths") -> str
  Imports:
    - from pathlib import Path                            [stdlib]
    - from typing import Any, Tuple                       [stdlib]
    - import numpy as np                                  [third_party]
    - from layers.layer_0_core.level_0 import get_logger  [internal — layer_0_core]
    - from layers.layer_0_core.level_1 import cleanup_gpu_memory, get_device  [internal — layer_0_core]
    - from layers.layer_0_core.level_2 import FeatureExtractor  [internal — layer_0_core]
    - from layers.layer_0_core.level_4 import load_json  [internal — layer_0_core]
    - from layers.layer_0_core.level_6 import create_test_dataloader  [internal — layer_0_core]
    - from layers.layer_1_competition.level_0_infra.level_1 import create_feature_extraction_model  [internal — competition_infra level_1]
  Line count: 122
  __all__: (none explicit)
```

```
FILE: level_2/registry/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .cli_handlers import get_cli_handlers_module, list_contests_with_cli_handlers, register_cli_handlers_module  [internal]
  Line count: 18
  __all__: ["get_cli_handlers_module", "list_contests_with_cli_handlers", "register_cli_handlers_module"]
```

```
FILE: level_2/registry/cli_handlers.py
  Module docstring: Contest CLI handler module registry (stored in ContestRegistry entries).
  Classes: (none)
  Functions:
    - register_cli_handlers_module(contest: str, module_path: str) -> None
    - list_contests_with_cli_handlers() -> List[str]
    - get_cli_handlers_module(contest: str) -> ModuleType
  Imports:
    - import importlib                                     [stdlib]
    - from types import ModuleType                         [stdlib]
    - from typing import List                              [stdlib]
    - from layers.layer_1_competition.level_0_infra.level_1 import ContestRegistry  [internal — competition_infra level_1]
  Line count: 52
  __all__: (none explicit)
```

---

#### 3. __init__.py Public API Summary

```
INIT: level_2/__init__.py
  Exports: (combined) FeatureExtractionHelper, extract_test_features_from_model, find_feature_filename_from_ensemble_metadata, get_cli_handlers_module, list_contests_with_cli_handlers, register_cli_handlers_module
  Re-exports from: level_2.feature_extraction, level_2.registry (via submodule __all__)
```

```
INIT: level_2/feature_extraction/__init__.py
  Exports: FeatureExtractionHelper, extract_test_features_from_model, find_feature_filename_from_ensemble_metadata
  Re-exports from: level_2.feature_extraction.feature_extraction_helper, level_2.feature_extraction.test_extractor
```

```
INIT: level_2/registry/__init__.py
  Exports: get_cli_handlers_module, list_contests_with_cli_handlers, register_cli_handlers_module
  Re-exports from: level_2.registry.cli_handlers
```

---

#### 4. Import Dependency Map

```
INTERNAL IMPORTS SUMMARY (sources referenced from this level package):
  From layers.layer_0_core:
    - level_0: get_logger
    - level_1: cleanup_gpu_memory, get_device
    - level_2: FeatureExtractor
    - level_4: load_json (inside find_feature_filename_from_ensemble_metadata)
    - level_6: create_test_dataloader
  From layers.layer_1_competition.level_0_infra:
    - level_1: ContestRegistry, create_feature_extraction_model
  Relative in logic files: none (only package-relative imports appear in __init__.py barrels)
  From level_2 toward same tier via absolute infra paths: none-only (no self-tier deep `level_2.*` imports in logic files beyond cross-subpackages via package root)
  Upward within level_0_infra (higher numeric tier importing this level): not applicable as source; this level does not import level_3+ infra
```

---

#### 5. Flags

```
FLAGS:
  level_2/README.md, level_2/feature_extraction/README.md, level_2/registry/README.md — present (non-Python)
```

---

#### 6. Static scan summary (precheck)

- **INFRA_TIER_UPWARD:** 0 files
- **INFRA_GENERAL_LEVEL:** 0 files
- **DEEP_PATH:** 0 files
- **RELATIVE_IN_LOGIC:** 0 files
- **PARSE_ERROR:** 0 files
- Precheck listed all Python modules under this scan root as clean files (six paths under `scripts/layers/layer_1_competition/level_0_infra/level_2/`).
