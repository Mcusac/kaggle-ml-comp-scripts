---
generated: 2026-04-08
audit_scope: competition_infra
level_name: level_0
pass_number: 1
artifact_kind: inventory
audit_profile: full
run_id: comp_infra_overhaul_2026-04-08
precheck_report_path: summaries/precheck_level_0_2026-04-08.md
---

# INVENTORY: level_0

#### 1. Package & File Tree

```
level_0/
  README.md
  __init__.py
  abstractions/ (README: yes)
    __init__.py
    contest_abstractions.py
    run_paths_protocol.py
  artifacts/ (README: yes)
    __init__.py
    schema.py
  cli/ (README: yes)
    __init__.py
    parser_helpers.py
  contest/ (README: yes)
    __init__.py
    config.py
    data_schema.py
    hierarchy.py
    ontology.py
    path_config.py
    paths.py
    post_processor.py
  model/ (README: yes)
    __init__.py
    embeddings.py
    feature_catalog.py
    model_constants.py
    verify_export_output.py
  paths/ (README: yes)
    __init__.py
    contest_output.py
    metadata_fallback.py
  pipeline/ (README: yes)
    __init__.py
    contest_training_config.py
    pipeline_kwargs.py
  registry/ (README: yes)
    __init__.py
  submission/ (README: yes)
    __init__.py
    strategy_validation.py
```

#### 2. Per-File Details

```
FILE: level_0/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from . import abstractions, artifacts, cli, contest, model, paths, pipeline, registry, submission [internal — subpackages]
    - from .abstractions import * [internal]
    - from .artifacts import * [internal]
    - from .cli import * [internal]
    - from .contest import * [internal]
    - from .model import * [internal]
    - from .paths import * [internal]
    - from .pipeline import * [internal]
    - from .registry import * [internal]
    - from .submission import * [internal]
  Line count: 35
  __all__: tuple expression concatenating subpackages' __all__ lists (abstractions, artifacts, cli, contest, model, paths, pipeline, registry, submission)

FILE: level_0/abstractions/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .contest_abstractions import ContestInputValidator, ContestMetric, ContestPipelineProtocol [internal]
    - from .run_paths_protocol import ContestRunPathsProtocol [internal]
    - from layers.layer_0_core.level_0 import PipelineResult [internal — layer_0_core]
  Line count: 18
  __all__: ["ContestInputValidator", "ContestMetric", "ContestPipelineProtocol", "ContestRunPathsProtocol", "PipelineResult"]

FILE: level_0/abstractions/contest_abstractions.py
  Classes:
    - ContestPipelineProtocol(Protocol)
        Methods: train_pipeline(self, data_root: str, **kwargs: Any) -> Optional[Path]
                 submit_pipeline(self, data_root: str, strategy: str, **kwargs: Any) -> Path
                 tune_pipeline(self, data_root: str, **kwargs: Any) -> Optional[Path]
    - ContestInputValidator(Protocol)
        Methods: validate_inputs(self, data_root: str, **kwargs: Any) -> None
    - ContestMetric(Protocol)
        Methods: compute(self, y_pred: Any, y_true: Any, config: Optional[Any] = None, **kwargs: Any) -> Tuple[float, Any]
  Functions: (none)
  Imports:
    - from pathlib import Path [stdlib]
    - from typing import Any, Optional, Protocol, Tuple [stdlib]
  Line count: 46
  __all__: (none)

FILE: level_0/abstractions/run_paths_protocol.py
  Classes:
    - ContestRunPathsProtocol(Protocol)
        Methods: get_output_dir(self) -> Path
  Functions: (none)
  Imports:
    - from pathlib import Path [stdlib]
    - from typing import Protocol [stdlib]
  Line count: 12
  __all__: (none)

FILE: level_0/artifacts/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .schema import ArtifactKeys, artifacts_merge, capture_config_paths, capture_metrics_paths, capture_model_paths, capture_submission_paths, metadata_merge [internal]
  Line count: 24
  __all__: ["ArtifactKeys", "artifacts_merge", "capture_config_paths", "capture_metrics_paths", "capture_model_paths", "capture_submission_paths", "metadata_merge"]

FILE: level_0/artifacts/schema.py
  Classes:
    - ArtifactKeys
        (class attributes string constants: TRAIN_CONFIG_JSON, TRAIN_METADATA_JSON, BEST_CONFIG_JSON, MODELS_DIR, MODEL_DIR, MODEL_CHECKPOINT, SUBMISSION_JSON, SUBMISSION_CSV, METRICS_JSON, METRICS_CSV)
  Functions:
    - artifacts_merge(*parts: Optional[Mapping[str, str]]) -> Dict[str, str]
    - metadata_merge(*parts: Optional[Mapping[str, Any]]) -> Dict[str, Any]
    - capture_config_paths(*, train_config_json: str | None = None, train_metadata_json: str | None = None, best_config_json: str | None = None) -> Dict[str, str]
    - capture_model_paths(*, models_dir: str | None = None, model_dir: str | None = None, model_checkpoint: str | None = None) -> Dict[str, str]
    - capture_submission_paths(*, submission_json: str | None = None, submission_csv: str | None = None) -> Dict[str, str]
    - capture_metrics_paths(*, metrics_json: str | None = None, metrics_csv: str | None = None) -> Dict[str, str]
  Imports:
    - from typing import Any, Dict, Mapping, Optional [stdlib]
  Line count: 109
  __all__: (none)

FILE: level_0/cli/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .parser_helpers import add_grid_search_parsers, add_training_parsers, add_ensemble_parsers, add_submission_parsers [internal]
  Line count: 15
  __all__: ["add_grid_search_parsers", "add_training_parsers", "add_ensemble_parsers", "add_submission_parsers"]

FILE: level_0/cli/parser_helpers.py
  Classes: (none)
  Functions:
    - add_grid_search_parsers(subparsers: Any, _add_common: Any) -> None
    - add_training_parsers(subparsers: Any, _add_common: Any) -> None
    - add_ensemble_parsers(subparsers: Any, _add_common: Any) -> None
    - add_submission_parsers(subparsers: Any, _add_common: Any) -> None
  Imports:
    - from typing import Any [stdlib]
  Line count: 131
  __all__: (none)

FILE: level_0/contest/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .config import ContestConfig [internal]
    - from .data_schema import ContestDataSchema [internal]
    - from .paths import ContestPaths [internal]
    - from .post_processor import ContestPostProcessor, ClipRangePostProcessor [internal]
    - from .ontology import ContestOntologySystem [internal]
    - from .hierarchy import ContestHierarchy [internal]
    - from .path_config import ContestPathConfig [internal]
  Line count: 20
  __all__: ["ContestConfig", "ContestDataSchema", "ContestPaths", "ContestPostProcessor", "ClipRangePostProcessor", "ContestOntologySystem", "ContestHierarchy", "ContestPathConfig"]

FILE: level_0/contest/config.py
  Classes:
    - ContestConfig(ABC)
        Properties (abstract): target_weights(self) -> Dict[str, float]
                               target_order(self) -> List[str]
                               primary_targets(self) -> List[str]
                               derived_targets(self) -> List[str]
        Properties (concrete): all_targets(self) -> List[str]
                               num_primary_targets(self) -> int
                               num_total_targets(self) -> int
                               constraint_matrix(self) -> Optional[np.ndarray]
        Methods: compute_derived_targets(self, predictions: np.ndarray) -> np.ndarray
  Functions: (none)
  Imports:
    - import numpy as np [third-party]
    - from abc import ABC, abstractmethod [stdlib]
    - from typing import Dict, List, Optional [stdlib]
  Line count: 120
  __all__: (none)

FILE: level_0/contest/data_schema.py
  Classes:
    - ContestDataSchema(ABC)
        Properties (abstract): sample_id_column(self) -> str
                               target_columns(self) -> List[str]
        Properties (concrete): feature_columns(self) -> Optional[List[str]]
        Methods (abstract): validate_sample_id(self, sample_id: str) -> bool
        Methods (concrete): get_sample_weights(self, sample_ids: List[str]) -> Optional[np.ndarray]
  Functions: (none)
  Imports:
    - import numpy as np [third-party]
    - from abc import ABC, abstractmethod [stdlib]
    - from typing import List, Optional [stdlib]
  Line count: 73
  __all__: (none)

FILE: level_0/contest/hierarchy.py
  Classes:
    - ContestHierarchy(ABC)
        Methods (abstract): get_ancestors(self, node_id: str) -> Set[str]
                            get_descendants(self, node_id: str) -> Set[str]
                            get_parents(self, node_id: str) -> Set[str]
                            get_children(self, node_id: str) -> Set[str]
        Methods (concrete): propagate_labels(self, labels: np.ndarray, label_ids: List[str]) -> np.ndarray
  Functions: (none)
  Imports:
    - import numpy as np [third-party]
    - from abc import ABC, abstractmethod [stdlib]
    - from typing import List, Set [stdlib]
  Line count: 95
  __all__: (none)

FILE: level_0/contest/ontology.py
  Classes:
    - ContestOntologySystem(ABC)
        Properties (abstract): ontology_codes(self) -> List[str]
                               ontology_names(self) -> Dict[str, str]
        Methods (abstract): get_ontology_config(self, ontology_code: str) -> Dict[str, Any]
        Methods (concrete): validate_ontology_code(self, ontology_code: str) -> bool
  Functions: (none)
  Imports:
    - from abc import ABC, abstractmethod [stdlib]
    - from typing import List, Dict, Any [stdlib]
  Line count: 64
  __all__: (none)

FILE: level_0/contest/path_config.py
  Classes:
    - ContestPathConfig (@dataclass)
        Fields: data_root, train_csv, test_csv, output_dir, model_dir, log_dir, submission_dir, cache_dir, feature_cache_dir, model_cache_dir (typed per dataclass)
  Functions: (none)
  Imports:
    - from dataclasses import dataclass [stdlib]
    - from typing import Optional [stdlib]
  Line count: 25
  __all__: (none)

FILE: level_0/contest/paths.py
  Classes:
    - ContestPaths(ABC)
        Properties (abstract): kaggle_dataset_name(self) -> str
                               kaggle_competition_name(self) -> Optional[str]
                               local_data_path(self) -> str
        Properties (concrete): kaggle_input_path(self) -> str
                               kaggle_working_path(self) -> str
                               local_data_root(self) -> Path
        Methods (concrete): get_data_root(self) -> Path
                            get_output_dir(self) -> Path
                            get_models_base_dir(self) -> Path
  Functions: (none)
  Imports:
    - from abc import ABC, abstractmethod [stdlib]
    - from pathlib import Path [stdlib]
    - from typing import Optional [stdlib]
    - from layers.layer_0_core.level_0 import is_kaggle [internal — layer_0_core]
    - from layers.layer_0_core.level_5 import find_project_input_root [internal — layer_0_core]
  Line count: 124
  __all__: (none)

FILE: level_0/contest/post_processor.py
  Classes:
    - ContestPostProcessor(ABC)
        Methods (abstract): apply(self, predictions: np.ndarray) -> np.ndarray
        Methods (concrete): enforce_constraints(self, predictions: np.ndarray) -> np.ndarray
                            clip_values(self, predictions: np.ndarray, min_val: float = None, max_val: float = None) -> np.ndarray
    - ClipRangePostProcessor(ContestPostProcessor)
        Methods: __init__(self, clip_min: float = 0.0, clip_max: float = 1.0)
                 apply(self, predictions: np.ndarray) -> np.ndarray
  Functions: (none)
  Imports:
    - import numpy as np [third-party]
    - from abc import ABC, abstractmethod [stdlib]
  Line count: 81
  __all__: (none)

FILE: level_0/model/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .embeddings import load_embedding_data, load_structured_features [internal]
    - from .feature_catalog import register_features [internal]
    - from .model_constants import MODEL_ID_MAP, get_model_image_size, get_model_name_from_pretrained, get_pretrained_weights_path [internal]
    - from .verify_export_output import verify_export_output [internal]
    - from layers.layer_0_core.level_1 import get_model_id [internal — layer_0_core]
  Line count: 25
  __all__: ["MODEL_ID_MAP", "get_model_id", "get_model_image_size", "get_model_name_from_pretrained", "get_pretrained_weights_path", "load_embedding_data", "load_structured_features", "register_features", "verify_export_output"]

FILE: level_0/model/embeddings.py
  Classes: (none)
  Functions:
    - load_embedding_data(embedding_type: str, datatype: str = "train", use_memmap: Optional[bool] = None, base_path: Optional[Path] = None) -> Tuple[np.ndarray, List[str]]
    - load_structured_features(feature_type: str, datatype: str = "train", use_memmap: Optional[bool] = None, base_path: Optional[Path] = None) -> Tuple[np.ndarray, List[str]]
  Imports:
    - import numpy as np [third-party]
    - from pathlib import Path [stdlib]
    - from typing import List, Optional, Tuple [stdlib]
    - from layers.layer_0_core.level_0 import get_logger [internal — layer_0_core]
  Line count: 36
  __all__: (none)

FILE: level_0/model/feature_catalog.py
  Classes: (none)
  Functions:
    - register_features() -> None
  Imports:
    - from layers.layer_0_core.level_0 import get_logger [internal — layer_0_core]
    - from layers.layer_0_core.level_1 import FEATURE_PRESETS, INDIVIDUAL_FEATURES [internal — layer_0_core]
  Line count: 89
  __all__: (none)

FILE: level_0/model/model_constants.py
  Classes: (none)
  Functions:
    - get_pretrained_weights_path(model_name: str) -> str
    - get_model_name_from_pretrained(pretrained_path: str) -> Optional[str]
    - get_model_image_size(model_name: str) -> Tuple[int, int]
  Imports:
    - from typing import Dict, Optional, Tuple [stdlib]
    - from layers.layer_0_core.level_1 import set_model_id_map [internal — layer_0_core]
  Module-level: MODEL_ID_MAP: Dict[str, str] ; module executes set_model_id_map(MODEL_ID_MAP) at import time
  Line count: 110
  __all__: (none)

FILE: level_0/model/verify_export_output.py
  Classes: (none)
  Functions:
    - verify_export_output(model_type: str = 'end_to_end') -> bool
  Imports:
    - from pathlib import Path [stdlib]
    - from layers.layer_0_core.level_0 import verify_export_files [internal — layer_0_core]
  Module-level: KAGGLE_EXPORT_DIR = Path('/kaggle/working/best_model')
  Line count: 21
  __all__: (none)

FILE: level_0/paths/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .contest_output import contest_models_dir [internal]
    - from .metadata_fallback import load_feature_filename_from_gridsearch [internal]
  Line count: 9
  __all__: ["contest_models_dir", "load_feature_filename_from_gridsearch"]

FILE: level_0/paths/contest_output.py
  Classes: (none)
  Functions:
    - contest_models_dir(paths: ContestPaths, contest_slug: str) -> Path
  Imports:
    - from pathlib import Path [stdlib]
    - from layers.layer_1_competition.level_0_infra.level_0 import ContestPaths [internal — same competition_infra level_0 barrel]
  Line count: 10
  __all__: (none)

FILE: level_0/paths/metadata_fallback.py
  Classes: (none)
  Functions:
    - load_feature_filename_from_gridsearch(variant_id: str, regression_model_type: str, metadata: Dict[str, Any], contest_context: Any = None) -> Optional[str]
  Imports:
    - from typing import Dict, Any, Optional [stdlib]
    - from layers.layer_0_core.level_0 import get_logger [internal — layer_0_core]
  Line count: 70
  __all__: (none)

FILE: level_0/pipeline/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .contest_training_config import create_training_config [internal]
    - from .pipeline_kwargs import create_pipeline_kwargs [internal]
  Line count: 9
  __all__: ["create_pipeline_kwargs", "create_training_config"]

FILE: level_0/pipeline/contest_training_config.py
  Classes: (none)
  Functions:
    - create_training_config(batch_size: int, num_epochs: int, learning_rate: float, optimizer: str, loss_function: str, scheduler: str, config) -> Dict[str, Any]
  Imports:
    - from typing import Dict, Any [stdlib]
    - from layers.layer_0_core.level_0 import build_training_config [internal — layer_0_core]
  Module-level: DEFAULT_TRAINING_SETTINGS: Dict[str, Any] (scheduler/early stopping/dataloader flags)
  Line count: 50
  __all__: (none)

FILE: level_0/pipeline/pipeline_kwargs.py
  Classes: (none)
  Functions:
    - create_pipeline_kwargs(paths: Any, data_schema: Any, model_type: str, image_subdir: Optional[str] = "images") -> dict
  Imports:
    - from typing import Any, Optional [stdlib]
  Line count: 35
  __all__: (none)

FILE: level_0/registry/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from layers.layer_0_core.level_0 import NamedRegistry, build_unknown_key_error [internal — layer_0_core]
  Line count: 13
  __all__: ["NamedRegistry", "build_unknown_key_error"]

FILE: level_0/submission/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .strategy_validation import validate_strategy_models [internal]
  Line count: 11
  __all__: ["validate_strategy_models"]

FILE: level_0/submission/strategy_validation.py
  Classes: (none)
  Functions:
    - validate_strategy_models(strategy: str, models: Sequence[str]) -> None
  Imports:
    - from typing import Sequence [stdlib]
  Line count: 23
  __all__: (none)
```

#### 3. __init__.py Public API Summary

```
INIT: level_0/__init__.py
  Exports: union of subpackage __all__ values (star-import aggregation from abstractions, artifacts, cli, contest, model, paths, pipeline, registry, submission).
  Re-exports from: level_0.abstractions, level_0.artifacts, level_0.cli, level_0.contest, level_0.model, level_0.paths, level_0.pipeline, level_0.registry, level_0.submission

INIT: level_0/abstractions/__init__.py
  Exports: ContestInputValidator, ContestMetric, ContestPipelineProtocol, ContestRunPathsProtocol, PipelineResult
  Re-exports from: level_0.abstractions.contest_abstractions, level_0.abstractions.run_paths_protocol, layers.layer_0_core.level_0 (PipelineResult)

INIT: level_0/artifacts/__init__.py
  Exports: ArtifactKeys, artifacts_merge, capture_config_paths, capture_metrics_paths, capture_model_paths, capture_submission_paths, metadata_merge
  Re-exports from: level_0.artifacts.schema

INIT: level_0/cli/__init__.py
  Exports: add_grid_search_parsers, add_training_parsers, add_ensemble_parsers, add_submission_parsers
  Re-exports from: level_0.cli.parser_helpers

INIT: level_0/contest/__init__.py
  Exports: ContestConfig, ContestDataSchema, ContestPaths, ContestPostProcessor, ClipRangePostProcessor, ContestOntologySystem, ContestHierarchy, ContestPathConfig
  Re-exports from: level_0.contest.* modules

INIT: level_0/model/__init__.py
  Exports: MODEL_ID_MAP, get_model_id, get_model_image_size, get_model_name_from_pretrained, get_pretrained_weights_path, load_embedding_data, load_structured_features, register_features, verify_export_output
  Re-exports from: level_0.model.embeddings, level_0.model.feature_catalog, level_0.model.model_constants, level_0.model.verify_export_output, layers.layer_0_core.level_1 (get_model_id)

INIT: level_0/paths/__init__.py
  Exports: contest_models_dir, load_feature_filename_from_gridsearch
  Re-exports from: level_0.paths.contest_output, level_0.paths.metadata_fallback

INIT: level_0/pipeline/__init__.py
  Exports: create_pipeline_kwargs, create_training_config
  Re-exports from: level_0.pipeline.contest_training_config, level_0.pipeline.pipeline_kwargs

INIT: level_0/registry/__init__.py
  Exports: NamedRegistry, build_unknown_key_error
  Re-exports from: layers.layer_0_core.level_0

INIT: level_0/submission/__init__.py
  Exports: validate_strategy_models
  Re-exports from: level_0.submission.strategy_validation
```

#### 4. Import Dependency Map

```
INTERNAL IMPORTS SUMMARY:
  From layers.layer_0_core.level_0:
    PipelineResult (abstractions/__init__.py)
    is_kaggle (contest/paths.py)
    get_logger (model/feature_catalog.py, model/embeddings.py, paths/metadata_fallback.py)
    verify_export_files (model/verify_export_output.py)
    build_training_config (pipeline/contest_training_config.py)
    NamedRegistry, build_unknown_key_error (registry/__init__.py)
  From layers.layer_0_core.level_1:
    FEATURE_PRESETS, INDIVIDUAL_FEATURES (model/feature_catalog.py)
    set_model_id_map (model/model_constants.py)
    get_model_id (model/__init__.py re-export)
  From layers.layer_0_core.level_5:
    find_project_input_root (contest/paths.py)
  From same competition_infra package (level_0_infra.level_0 barrel):
    ContestPaths (paths/contest_output.py) — imports `layers.layer_1_competition.level_0_infra.level_0`; auditor: same-tier barrel surface / cycle risk vs relative `contest.paths` import style
  From layers.layer_1_competition.level_0_infra.level_1 or contests/* or level_1_impl:
    (none observed in this level_0 tree)
  Relative imports in __init__.py files only:
    Root and subpackage __init__.py files use `from .` aggregation per package pattern; logic modules use absolute `layers.*` except subpackage __init__ files.
```

#### 5. Flags

```
FLAGS:
  paths/contest_output.py — imports ContestPaths from top-level `layers.layer_1_competition.level_0_infra.level_0` barrel while residing under same package; name collision domain: subpackage `paths/` vs module `contest/paths.py` (distinct symbols, same vocabulary).
  model/embeddings.py — `load_embedding_data` / `load_structured_features` raise NotImplementedError (framework placeholders).
  model/verify_export_output.py — uses print() to stdout with emoji markers for user-facing export verification messages.
  model/model_constants.py — calls `set_model_id_map(MODEL_ID_MAP)` at import time (global side effect in infra tier).
  cli/parser_helpers.py — filename segment `helpers` (not a package named utils/helpers/misc/common).
  Small __init__ files: paths/__init__.py (9 lines), pipeline/__init__.py (9 lines), paths/contest_output.py (10 lines).
  No single .py file exceeds 300 lines in this inventory (largest: cli/parser_helpers.py at 131 lines).
  No matches in *.py for deprecated | legacy | compat | backwards | TODO: remove | shim (case-insensitive grep).
  Duplicate simple class/function names across files: `apply` on post-processors only; no duplicate top-level public type names across modules except intentional ABC family in contest/.
```

#### 6. Static scan summary (precheck)

```
Source: summaries/precheck_level_0_2026-04-08.md (precheck_status: skipped_machine_script)
- Machine-backed Phase 7 / static reconciliation did not run: environment raised ModuleNotFoundError for `layers.layer_2_devtools.level_0_infra.level_0.path.level_paths` while loading the precheck script path.
- Precheck markdown recommends installing/enabling optional local dependencies (example cited: torchvision) and rerunning precheck for machine-backed reconciliation.
- No per-file violation rows from scan machinery for this pass — inventory §2–§4 are authoritative for structure and imports.
```
