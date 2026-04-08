---
generated: 2026-04-08
audit_scope: general
level_name: level_0
pass_number: 1
run_id: general-stack-orchestrator-2026-04-08
artifact_kind: inventory
audit_profile: full
---

# INVENTORY: level_0

## 1. Package & File Tree

```
level_0/
  README.md
  __init__.py
  abstractions/
    README.md
    __init__.py
    ensembling_method.py
    grid_search_context.py
    handler_context_builder.py
    metric.py
    model_registry.py
    named_registry.py
    pipeline_result.py
  cli/
    README.md
    __init__.py
    args_utils.py
    argument_groups.py
    commands.py
    common_args.py
    dispatcher.py
  config/
    README.md
    __init__.py
    base_schema.py
    data_split.py
    extractor.py
    pipeline_config.py
    runtime_config.py
    training_cadence.py
    training_modes.py
  embeddings/
    README.md
    __init__.py
    alignment.py
    id_ops.py
    normalize.py
    path_resolver.py
  errors/
    README.md
    __init__.py
    config_errors.py
    data_errors.py
    model_errors.py
    pipeline_errors.py
    runtime_errors.py
  grid_search/
    README.md
    __init__.py
    combinatorics.py
    constants.py
    grid_engine.py
    param_space.py
    result_builders.py
    result_selection.py
    results_payload.py
    varied_params.py
  ontology/
    README.md
    __init__.py
    obo_parser.py
  paths/
    README.md
    __init__.py
    filesystem.py
    fold_paths.py
  prediction_guards/
    README.md
    __init__.py
    arrays.py
    lists.py
    policies.py
    submission.py
    verify_export_files.py
  protein_features/
    README.md
    __init__.py
    amino_acid_constants.py
    kmer_features.py
  runtime/
    README.md
    __init__.py
    base_command_builder.py
    cache_paths.py
    environment_setup.py
    execution_result.py
    log_configure.py
    platform_detection.py
    run_command_stream.py
    runtime_types.py
    torch_guard.py
  scoring/
    README.md
    __init__.py
    calculate_percentile_weights.py
    combine_predictions.py
    ensemble_weights.py
  training/
    README.md
    __init__.py
    build_config.py
    epoch_history.py
    extract_batch_data.py
    scheduler.py
  vision/
    README.md
    __init__.py
    minimal_val_transform.py
    model_path.py
    model_type.py
    noise_reduction.py
    transform_constants.py
    transform_defaults.py
    transform_mode.py
    image/
      README.md
      __init__.py
      config.py
      loading.py
      patching.py
```

## 2. Per-File Details

```
FILE: __init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from . import abstractions                    [internal · level_0]
    - from . import cli                              [internal · level_0]
    - from . import config                           [internal · level_0]
    - from . import embeddings                       [internal · level_0]
    - from . import errors                           [internal · level_0]
    - from . import grid_search                      [internal · level_0]
    - from . import ontology                         [internal · level_0]
    - from . import paths                             [internal · level_0]
    - from . import prediction_guards                 [internal · level_0]
    - from . import protein_features                  [internal · level_0]
    - from . import runtime                           [internal · level_0]
    - from . import scoring                           [internal · level_0]
    - from . import training                         [internal · level_0]
    - from . import vision                            [internal · level_0]
    - from .abstractions import *                    [internal · level_0]
    - from .cli import *                             [internal · level_0]
    - from .config import *                          [internal · level_0]
    - from .embeddings import *                      [internal · level_0]
    - from .errors import *                          [internal · level_0]
    - from .grid_search import *                     [internal · level_0]
    - from .ontology import *                        [internal · level_0]
    - from .paths import *                           [internal · level_0]
    - from .prediction_guards import *               [internal · level_0]
    - from .protein_features import *               [internal · level_0]
    - from .runtime import *                         [internal · level_0]
    - from .scoring import *                         [internal · level_0]
    - from .training import *                        [internal · level_0]
    - from .vision import *                          [internal · level_0]
  Line count: 48
  __all__: tuple expression concatenating subpackage __all__ lists (see source)
```

```
FILE: abstractions/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .ensembling_method import EnsemblingMethod              [internal]
    - from .grid_search_context import GridSearchContext            [internal]
    - from .handler_context_builder import HandlerContextBuilder  [internal]
    - from .metric import Metric                                  [internal]
    - from .model_registry import ModelRegistry                     [internal]
    - from .named_registry import NamedRegistry, build_unknown_key_error  [internal]
    - from .pipeline_result import PipelineResult                 [internal]
  Line count: 20
  __all__: ['EnsemblingMethod', 'GridSearchContext', 'HandlerContextBuilder', 'Metric', 'ModelRegistry', 'NamedRegistry', 'build_unknown_key_error', 'PipelineResult']
```

```
FILE: abstractions/ensembling_method.py
  Classes:
    - EnsemblingMethod(ABC)
        Methods: combine(self, predictions_list: List[np.ndarray], weights: Optional[List[float]] = None) -> np.ndarray
                 get_name(self) -> str
  Functions: (none)
  Imports:
    - import numpy as np                             [third-party]
    - from abc import ABC, abstractmethod            [stdlib]
    - from typing import List, Optional              [stdlib]
  Line count: 38
  __all__: (none)
```

```
FILE: abstractions/grid_search_context.py
  Classes:
    - GridSearchContext(Protocol)
        Methods: get_paths(self) -> Any
                 get_config(self) -> Any
                 get_metric_calculator(self) -> Callable[..., float]
                 get_metadata_handler(self) -> Any
                 get_feature_cache_loader(self) -> Any
                 get_parameter_grid_fn(self) -> Callable[..., Any]
  Functions: (none)
  Imports:
    - from typing import Any, Callable, Protocol   [stdlib]
  Line count: 31
  __all__: (none)
```

```
FILE: abstractions/handler_context_builder.py
  Classes:
    - HandlerContextBuilder(Protocol)
        Methods: detect_contest(self, args: argparse.Namespace) -> str
                 get_config(self, contest_name: str, args: argparse.Namespace) -> Any
                 get_paths(self, contest_name: str) -> Any
                 get_data_schema(self, contest_name: str) -> Any
                 load_contest_data(self, contest_name: str, model_type: str, **kwargs: Any) -> Tuple[Any, Any, Any]
  Functions: (none)
  Imports:
    - from typing import Any, Protocol, Tuple        [stdlib]
    - import argparse                                [stdlib]
  Line count: 36
  __all__: (none)
```

```
FILE: abstractions/metric.py
  Classes:
    - Metric(ABC)
        Methods: __init__(self, name: str)
                 calculate(self, y_true: np.ndarray, y_pred: np.ndarray, **kwargs) -> Union[float, Dict[str, float]]
                 __call__(self, y_true: np.ndarray, y_pred: np.ndarray, **kwargs) -> Union[float, Dict[str, float]]
                 __repr__(self) -> str
  Functions: (none)
  Imports:
    - import numpy as np                             [third-party]
    - from abc import ABC, abstractmethod           [stdlib]
    - from typing import Dict, Union                 [stdlib]
  Line count: 37
  __all__: (none)
```

```
FILE: abstractions/model_registry.py
  Classes:
    - ModelRegistry
        Methods: register(cls, model_type: str, factory: Callable[..., Any]) -> None
                 create(cls, model_type: str, **kwargs: Any) -> Any
                 is_registered(cls, model_type: str) -> bool
  Functions: (none)
  Imports:
    - from typing import Any, Callable, Dict         [stdlib]
  Line count: 34
  __all__: (none)
```

```
FILE: abstractions/named_registry.py
  Classes:
    - NamedRegistry(Generic[T])  [dataclass]
        Fields: registry_name: str, key_label: str, _items: Dict[str, T]
        Methods: register(self, key: str) -> Callable[[T], T]
                 set(self, key: str, obj: T) -> None
                 get(self, key: str) -> Optional[T]
                 require(self, key: str) -> T
                 list_keys(self) -> list[str]
                 contains(self, key: str) -> bool
                 bulk_validate_known(self, keys: Iterable[str]) -> None
  Functions:
    - build_unknown_key_error(*, registry_name: str, key_label: str, key: str, available: Sequence[str]) -> str
  Imports:
    - from dataclasses import dataclass, field       [stdlib]
    - from typing import Callable, Dict, Generic, Iterable, Optional, Sequence, TypeVar  [stdlib]
  Line count: 72
  __all__: (none)
```

```
FILE: abstractions/pipeline_result.py
  Classes:
    - PipelineResult  [frozen dataclass]
        Fields: success: bool, stage: str, error: str | None, artifacts: Mapping[str, str], metadata: Mapping[str, Any]
        Methods: ok(*, stage: str, artifacts: Mapping[str, str] | None = None, metadata: Mapping[str, Any] | None = None) -> PipelineResult  [staticmethod]
                 fail(*, stage: str, error: str, artifacts: Mapping[str, str] | None = None, metadata: Mapping[str, Any] | None = None) -> PipelineResult  [staticmethod]
  Functions: (none)
  Imports:
    - from dataclasses import dataclass, field       [stdlib]
    - from typing import Any, Mapping                [stdlib]
  Line count: 46
  __all__: (none)
```

```
FILE: cli/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .args_utils import get_arg, parse_comma_separated, comma_separated_type, parse_key_value_pairs  [internal]
    - from .argument_groups import add_model_type_argument, add_model_path_argument, add_ensemble_method_argument  [internal]
    - from .commands import Command                 [internal]
    - from .common_args import add_common_arguments  [internal]
    - from .dispatcher import dispatch_command       [internal]
  Line count: 27
  __all__: ['get_arg', 'parse_comma_separated', 'comma_separated_type', 'parse_key_value_pairs', 'add_model_type_argument', 'add_model_path_argument', 'add_ensemble_method_argument', 'Command', 'add_common_arguments', 'dispatch_command']
```

```
FILE: cli/args_utils.py
  Classes: (none)
  Functions:
    - get_arg(args: Any, key: str, default: Any = None) -> Any
    - parse_comma_separated(value: Optional[str]) -> Optional[List[str]]
    - comma_separated_type(value: str) -> List[str]
    - parse_key_value_pairs(value: Optional[str], pair_sep: str = ',', kv_sep: str = '=') -> Optional[Dict[str, str]]
  Imports:
    - from typing import Any, List, Optional, Dict   [stdlib]
  Line count: 96
  __all__: (none)
```

```
FILE: cli/argument_groups.py
  Classes: (none)
  Functions:
    - add_model_type_argument(parser: argparse.ArgumentParser, model_type_choices: Sequence[str], default: str = 'vision') -> None
    - add_model_path_argument(parser: argparse.ArgumentParser, required: bool = False) -> None
    - add_ensemble_method_argument(parser: argparse.ArgumentParser, ensemble_methods: Sequence[str], default: str = 'weighted_average') -> None
  Imports:
    - import argparse                                [stdlib · argparse]
    - from typing import Sequence                    [stdlib]
  Line count: 42
  __all__: (none)
```

```
FILE: cli/commands.py
  Classes:
    - Command(Enum)
        Members: TRAIN, TEST, TRAIN_TEST, GRID_SEARCH, CROSS_VALIDATE, ENSEMBLE, EXPORT_MODEL
  Functions: (none)
  Imports:
    - from enum import Enum                          [stdlib]
  Line count: 15
  __all__: (none)
```

```
FILE: cli/common_args.py
  Classes: (none)
  Functions:
    - add_common_arguments(parser: argparse.ArgumentParser) -> None
  Imports:
    - import argparse                                [stdlib]
  Line count: 8
  __all__: (none)
```

```
FILE: cli/dispatcher.py
  Classes: (none)
  Functions:
    - dispatch_command(command: str, args: argparse.Namespace, primary_handlers: Dict[str, Callable[[argparse.Namespace], None]], fallback_handlers: Optional[Dict[str, Callable[[argparse.Namespace], None]]] = None) -> None
  Imports:
    - import argparse                                [stdlib]
    - from typing import Callable, Dict, Optional    [stdlib]
  Line count: 45
  __all__: (none)
```

```
FILE: config/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .base_schema import BaseConfig, TrainingSchema, EvaluationSchema, PathConfig, CompositeConfig  [internal]
    - from .extractor import get_config_value       [internal]
    - from .data_split import DataSplit              [internal]
    - from .pipeline_config import PipelineConfig    [internal]
    - from .runtime_config import RuntimeConfig      [internal]
    - from .training_cadence import TrainingCadenceConfig  [internal]
    - from .training_modes import TrainingMode       [internal]
  Line count: 29
  __all__: ['BaseConfig', 'TrainingSchema', 'EvaluationSchema', 'PathConfig', 'CompositeConfig', 'get_config_value', 'DataSplit', 'PipelineConfig', 'RuntimeConfig', 'TrainingCadenceConfig', 'TrainingMode']
```

```
FILE: config/base_schema.py
  Classes:
    - BaseConfig  [dataclass] — docstring only; no instance fields declared (pass)
    - TrainingSchema  [dataclass]
        Fields: batch_size: int = 32, epochs: int = 30, learning_rate: Optional[float] = None
    - EvaluationSchema  [dataclass]
        Fields: metric: str = ""
    - PathConfig  [dataclass]
        Fields: output_dir: Path, checkpoint_dir: Path  (default_factory)
    - CompositeConfig(BaseConfig)  [dataclass]
        Fields: training: TrainingSchema, evaluation: EvaluationSchema, paths: PathConfig  (default_factory)
  Functions: (none)
  Imports:
    - from dataclasses import dataclass, field       [stdlib]
    - from pathlib import Path                       [stdlib]
    - from typing import Optional                    [stdlib]
  Line count: 46
  __all__: (none)
```

```
FILE: config/data_split.py
  Classes:
    - DataSplit(Enum)
        Members: TRAIN, VAL, TEST
  Functions: (none)
  Imports:
    - from enum import Enum                          [stdlib]
  Line count: 11
  __all__: (none)
```

```
FILE: config/extractor.py
  Classes: (none)
  Functions:
    - get_config_value(config: Union[Any, Dict[str, Any]], path: str, default: Any = None, required: bool = False) -> Any
  Imports:
    - from typing import Any, Dict, Union            [stdlib]
  Line count: 70
  __all__: (none)
```

```
FILE: config/pipeline_config.py
  Classes:
    - PipelineConfig  [dataclass]
        Fields: grid_search_n_jobs, grid_search_verbose, grid_search_pre_dispatch, cv_n_folds, cv_shuffle, cv_random_state, ensemble_method, ensemble_n_models, ensemble_weights, export_format, export_include_metadata, checkpoint_dir, results_dir, logs_dir  (defaults per source)
        Methods: to_dict(self) -> Dict[str, Any]
  Functions: (none)
  Imports:
    - from dataclasses import dataclass              [stdlib]
    - from typing import Any, Dict, List, Optional   [stdlib]
  Line count: 53
  __all__: (none)
```

```
FILE: config/runtime_config.py
  Classes:
    - RuntimeConfig  [dataclass]
        Fields: seed, device, num_workers, output_dir, log_dir, verbose, debug  (defaults per source)
        Methods: __post_init__(self) -> None
  Functions: (none)
  Imports:
    - from dataclasses import dataclass              [stdlib]
    - from pathlib import Path                       [stdlib]
    - from typing import Optional                    [stdlib]
  Line count: 34
  __all__: (none)
```

```
FILE: config/training_cadence.py
  Classes:
    - TrainingCadenceConfig  [dataclass]
        Fields: log_every_n_steps, log_every_n_epochs, checkpoint_every_n_epochs, checkpoint_every_n_steps  (defaults per source)
  Functions: (none)
  Imports:
    - from dataclasses import dataclass              [stdlib]
    - from typing import Optional                    [stdlib]
  Line count: 14
  __all__: (none)
```

```
FILE: config/training_modes.py
  Classes:
    - TrainingMode(Enum)
        Members: LOAD_OR_TRAIN, TRAIN_NEW, LOAD_ONLY
  Functions: (none)
  Imports:
    - from enum import Enum                          [stdlib]
  Line count: 10
  __all__: (none)
```

```
FILE: embeddings/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .alignment import align_embeddings        [internal]
    - from .id_ops import find_common_ids              [internal]
    - from .normalize import normalize_embedding_type  [internal]
    - from .path_resolver import resolve_embedding_base_path  [internal]
  Line count: 13
  __all__: ['align_embeddings', 'find_common_ids', 'normalize_embedding_type', 'resolve_embedding_base_path']
```

```
FILE: embeddings/alignment.py
  Classes: (none)
  Functions:
    - align_embeddings(embeds: np.ndarray, embed_ids: List[str], target_ids: List[str]) -> Tuple[np.ndarray, List[str]]
  Imports:
    - import numpy as np                             [third-party]
    - from typing import List, Tuple                 [stdlib]
  Line count: 30
  __all__: (none)
```

```
FILE: embeddings/id_ops.py
  Classes: (none)
  Functions:
    - find_common_ids(embedding_list: List[Tuple[np.ndarray, List[str]]], target_ids: List[str]) -> List[str]
  Imports:
    - from typing import List, Tuple                 [stdlib]
    - import numpy as np                             [third-party]
  Line count: 30
  __all__: (none)
```

```
FILE: embeddings/normalize.py
  Classes: (none)
  Functions:
    - normalize_embedding_type(embedding_type: str, aliases: Optional[Dict[str, str]] = None) -> str
  Imports:
    - from typing import Dict, Optional              [stdlib]
  Line count: 18
  __all__: (none)
```

```
FILE: embeddings/path_resolver.py
  Classes: (none)
  Functions:
    - resolve_embedding_base_path(embedding_type: str, base_path: Optional[Path], paths_config: Dict[str, Path]) -> Path
  Imports:
    - from pathlib import Path                       [stdlib]
    - from typing import Dict, Optional              [stdlib]
  Line count: 33
  __all__: (none)
```

```
FILE: errors/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .config_errors import ConfigError, ConfigValidationError, ConfigLoadError  [internal]
    - from .data_errors import DataError, DataLoadError, DataValidationError, DataProcessingError  [internal]
    - from .model_errors import ModelError, ModelLoadError, ModelTrainingError, ModelPredictionError  [internal]
    - from .pipeline_errors import PipelineError, PipelineSetupError, PipelineExecutionError  [internal]
    - from .runtime_errors import CoreRuntimeError, DeviceError, EnvironmentConfigError, ProcessError, ExecutionError  [internal]
  Line count: 35
  __all__: ['ConfigError', 'ConfigValidationError', 'ConfigLoadError', 'DataError', 'DataLoadError', 'DataValidationError', 'DataProcessingError', 'ModelError', 'ModelLoadError', 'ModelTrainingError', 'ModelPredictionError', 'PipelineError', 'PipelineSetupError', 'PipelineExecutionError', 'CoreRuntimeError', 'DeviceError', 'EnvironmentConfigError', 'ProcessError', 'ExecutionError']
```

```
FILE: errors/config_errors.py
  Classes:
    - ConfigError(Exception)
    - ConfigValidationError(ConfigError)
    - ConfigLoadError(ConfigError)
  Functions: (none)
  Imports: (none at module level)
  Line count: 42
  __all__: (none)
```

```
FILE: errors/data_errors.py
  Classes:
    - DataError(Exception)
    - DataLoadError(DataError)
    - DataValidationError(DataError)
    - DataProcessingError(DataError)
  Functions: (none)
  Imports: (none at module level)
  Line count: 73
  __all__: (none)
```

```
FILE: errors/model_errors.py
  Classes:
    - ModelError(Exception)
    - ModelLoadError(ModelError)
    - ModelTrainingError(ModelError)
    - ModelPredictionError(ModelError)
  Functions: (none)
  Imports: (none at module level)
  Line count: 67
  __all__: (none)
```

```
FILE: errors/pipeline_errors.py
  Classes:
    - PipelineError(Exception)
    - PipelineSetupError(PipelineError)
    - PipelineExecutionError(PipelineError)
  Functions: (none)
  Imports: (none at module level)
  Line count: 50
  __all__: (none)
```

```
FILE: errors/runtime_errors.py
  Classes:
    - CoreRuntimeError(Exception)
    - DeviceError(Exception)
    - EnvironmentConfigError(Exception)
    - ProcessError(Exception)
    - ExecutionError(RuntimeError)
  Functions: (none)
  Imports: (none at module level)
  Line count: 30
  __all__: (none)
```

```
FILE: grid_search/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .combinatorics import generate_power_set  [internal]
    - from .constants import BEST_HYPERPARAMETERS_FILE, BEST_VARIANT_FILE_DATASET, DATASET_TYPE_FULL, DATASET_TYPE_SPLIT, DEFAULT_CLEANUP_INTERVAL, DEFAULT_KEEP_TOP_VARIANTS, FOCUSED_SEARCH_TYPES, GRID_SEARCH_TYPE_DATASET, GRID_SEARCH_TYPE_FIELD_DATASET, GRID_SEARCH_TYPE_FIELD_HYPERPARAMETER, GRID_SEARCH_TYPE_HYPERPARAMETER, MODEL_DIR_DATASET_GRID_SEARCH, MODEL_DIR_HYPERPARAMETER_GRID_SEARCH, RESULTS_FILE_GRIDSEARCH, SEARCH_TYPE_DEFAULTS, SEARCH_TYPE_FOCUSED_IN_DEPTH, SEARCH_TYPE_FOCUSED_THOROUGH, SEARCH_TYPE_IN_DEPTH, SEARCH_TYPE_QUICK, SEARCH_TYPE_THOROUGH, VALID_HYPERPARAMETER_SEARCH_TYPES  [internal]
    - from .grid_engine import build_parameter_grid, merge_focused_ranges_into_base_grid  [internal]
    - from .param_space import calculate_total_combinations, generate_param_combinations  [internal]
    - from .result_builders import create_error_result_dict, create_result_dict  [internal]
    - from .results_payload import extract_results_list  [internal]
    - from .result_selection import filter_results, filter_successful_results, get_best_variant, get_top_n_variants, worst_case_metric_sentinel  [internal]
    - from .varied_params import resolve_varied_params  [internal]
  Line count: 76
  __all__: ['generate_power_set', 'GRID_SEARCH_TYPE_DATASET', 'GRID_SEARCH_TYPE_HYPERPARAMETER', 'SEARCH_TYPE_DEFAULTS', 'SEARCH_TYPE_QUICK', 'SEARCH_TYPE_IN_DEPTH', 'SEARCH_TYPE_THOROUGH', 'SEARCH_TYPE_FOCUSED_IN_DEPTH', 'SEARCH_TYPE_FOCUSED_THOROUGH', 'VALID_HYPERPARAMETER_SEARCH_TYPES', 'FOCUSED_SEARCH_TYPES', 'DATASET_TYPE_FULL', 'DATASET_TYPE_SPLIT', 'RESULTS_FILE_GRIDSEARCH', 'GRID_SEARCH_TYPE_FIELD_DATASET', 'GRID_SEARCH_TYPE_FIELD_HYPERPARAMETER', 'BEST_VARIANT_FILE_DATASET', 'BEST_HYPERPARAMETERS_FILE', 'MODEL_DIR_DATASET_GRID_SEARCH', 'MODEL_DIR_HYPERPARAMETER_GRID_SEARCH', 'DEFAULT_KEEP_TOP_VARIANTS', 'DEFAULT_CLEANUP_INTERVAL', 'build_parameter_grid', 'merge_focused_ranges_into_base_grid', 'calculate_total_combinations', 'generate_param_combinations', 'get_best_variant', 'get_top_n_variants', 'filter_successful_results', 'worst_case_metric_sentinel', 'filter_results', 'create_result_dict', 'create_error_result_dict', 'extract_results_list', 'resolve_varied_params']
```

```
FILE: grid_search/combinatorics.py
  Classes: (none)
  Functions:
    - generate_power_set(items: List[T]) -> List[Tuple[T, ...]]
  Imports:
    - from typing import List, Tuple, TypeVar        [stdlib]
    - from itertools import combinations             [stdlib]
  Line count: 35
  __all__: (none)
```

```
FILE: grid_search/constants.py
  Classes: (none)
  Functions: (none)
  Imports: (none)
  Line count: 52
  __all__: (none)
  Module-level assignments: GRID_SEARCH_TYPE_DATASET, GRID_SEARCH_TYPE_HYPERPARAMETER, SEARCH_TYPE_*, VALID_HYPERPARAMETER_SEARCH_TYPES, FOCUSED_SEARCH_TYPES, DATASET_TYPE_*, RESULTS_FILE_GRIDSEARCH, GRID_SEARCH_TYPE_FIELD_*, BEST_VARIANT_FILE_DATASET, BEST_HYPERPARAMETERS_FILE, MODEL_DIR_*_GRID_SEARCH, DEFAULT_KEEP_TOP_VARIANTS, DEFAULT_CLEANUP_INTERVAL
```

```
FILE: grid_search/grid_engine.py
  Classes: (none)
  Functions:
    - build_parameter_grid(defaults: Dict[str, Any], varied_params: Dict[str, List[Any]]) -> Dict[str, List[Any]]
    - merge_focused_ranges_into_base_grid(base_grid: Dict[str, List[Any]], focused_ranges: Dict[str, List[Any]]) -> Dict[str, List[Any]]
  Imports:
    - from typing import Any, Dict, List             [stdlib]
  Line count: 30
  __all__: (none)
```

```
FILE: grid_search/param_space.py
  Classes: (none)
  Functions:
    - calculate_total_combinations(param_grid: Dict[str, List[Any]]) -> int
    - generate_param_combinations(param_grid: Dict[str, List[Any]]) -> Iterator[Dict[str, Any]]
  Imports:
    - import itertools                               [stdlib]
    - from typing import Dict, List, Any, Iterator   [stdlib]
  Line count: 55
  __all__: (none)
```

```
FILE: grid_search/result_builders.py
  Classes: (none)
  Functions:
    - create_result_dict(variant_index: int, variant_id: str, cv_score: Optional[float], fold_scores: Optional[List[float]], batch_size_used: int, batch_size_reduced: bool, variant_specific_data: Dict[str, Any]) -> Dict[str, Any]
    - create_error_result_dict(variant_index: int, variant_id: str, error: str, batch_size_used: Optional[int], batch_size_reduced: bool, variant_specific_data: Dict[str, Any], skipped: bool = False) -> Dict[str, Any]
  Imports:
    - from typing import Dict, Any, Optional, List   [stdlib]
  Line count: 75
  __all__: (none)
```

```
FILE: grid_search/result_selection.py
  Classes: (none)
  Functions:
    - filter_successful_results(results: List[Dict[str, Any]]) -> List[Dict[str, Any]]
    - worst_case_metric_sentinel(maximize: bool) -> float
    - get_best_variant(results: List[Dict[str, Any]], metric_key: str = 'score', maximize: bool = True) -> Dict[str, Any]
    - get_top_n_variants(results: List[Dict[str, Any]], n: int = 5, metric_key: str = 'score', maximize: bool = True) -> List[Dict[str, Any]]
    - filter_results(results: List[Dict[str, Any]], predicate: Callable[[Dict[str, Any]], bool]) -> List[Dict[str, Any]]
  Imports:
    - from typing import List, Dict, Any, Callable    [stdlib]
  Line count: 131
  __all__: (none)
```

```
FILE: grid_search/results_payload.py
  Classes: (none)
  Functions:
    - extract_results_list(data: Any) -> List[Dict]
  Imports:
    - from typing import Any, Dict, List             [stdlib]
  Line count: 12
  __all__: (none)
```

```
FILE: grid_search/varied_params.py
  Classes: (none)
  Functions:
    - resolve_varied_params(search_type: str, varied_by_search_type: Dict[str, Dict[str, List[Any]]]) -> Dict[str, List[Any]]
  Imports:
    - from typing import Any, Dict, List             [stdlib]
  Line count: 27
  __all__: (none)
```

```
FILE: ontology/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .obo_parser import parse_obo_file         [internal]
  Line count: 5
  __all__: ['parse_obo_file']
```

```
FILE: ontology/obo_parser.py
  Classes: (none)
  Functions:
    - parse_obo_file(obo_path: Path) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]
    - _parse_obo_manual(obo_path: Path) -> Tuple[Dict[str, Set[str]], Dict[str, Set[str]]]
  Imports (module level):
    - from collections import defaultdict            [stdlib]
    - from pathlib import Path                       [stdlib]
    - from typing import Dict, Set, Tuple           [stdlib]
  Imports (function-local): import obonet inside parse_obo_file (optional dependency)
  Line count: 75
  __all__: (none)
```

```
FILE: paths/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .filesystem import ensure_dir, normalize_path, get_file_size_mb, ensure_file_dir  [internal]
    - from .fold_paths import get_fold_checkpoint_path, get_fold_regression_model_path  [internal]
  Line count: 18
  __all__: ['ensure_dir', 'normalize_path', 'get_file_size_mb', 'ensure_file_dir', 'get_fold_checkpoint_path', 'get_fold_regression_model_path']
```

```
FILE: paths/filesystem.py
  Classes: (none)
  Functions:
    - ensure_dir(dirpath: Union[str, Path]) -> Path
    - normalize_path(path: Union[str, Path]) -> Path
    - get_file_size_mb(path: Union[str, Path]) -> float
    - ensure_file_dir(filepath: Union[str, Path]) -> Path
  Imports:
    - from pathlib import Path                       [stdlib]
    - from typing import Union                       [stdlib]
  Line count: 95
  __all__: (none)
```

```
FILE: paths/fold_paths.py
  Classes: (none)
  Functions:
    - _validate_fold_path_args(model_dir: Union[str, Path, None], fold: int) -> Path
    - _get_fold_dir(base: Path, fold: int) -> Path
    - get_fold_checkpoint_path(model_dir: Path, fold: int) -> Path
    - get_fold_regression_model_path(model_dir: Path, fold: int) -> Path
  Imports:
    - from pathlib import Path                       [stdlib]
    - from typing import Union                       [stdlib]
  Line count: 56
  __all__: (none)
```

```
FILE: prediction_guards/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .arrays import validate_predictions_shape, validate_targets  [internal]
    - from .lists import validate_predictions_list, validate_same_shape, get_shape_and_targets  [internal]
    - from .policies import NonNegativePredictionMixin  [internal]
    - from .submission import validate_submission_format, validate_go_term_format, is_valid_score  [internal]
    - from .verify_export_files import verify_export_files  [internal]
  Line count: 20
  __all__: ['validate_predictions_shape', 'validate_targets', 'validate_predictions_list', 'validate_same_shape', 'get_shape_and_targets', 'NonNegativePredictionMixin', 'validate_submission_format', 'validate_go_term_format', 'is_valid_score', 'verify_export_files']
```

```
FILE: prediction_guards/arrays.py
  Classes: (none)
  Functions:
    - validate_predictions_shape(predictions: np.ndarray, expected_count: int, expected_cols: int = 3) -> None
    - validate_targets(y_val: np.ndarray, n_samples: int, n_targets: int) -> None
  Imports:
    - import numpy as np                             [third-party]
  Line count: 60
  __all__: (none)
```

```
FILE: prediction_guards/lists.py
  Classes: (none)
  Functions:
    - validate_predictions_list(predictions_list: List[np.ndarray], name: str = 'predictions_list') -> None
    - validate_same_shape(predictions_list: List[np.ndarray], name: str = 'predictions_list') -> Tuple[int, ...]
    - get_shape_and_targets(predictions_list: List[np.ndarray]) -> Tuple[Tuple[int, ...], int]
  Imports:
    - from typing import List, Tuple                 [stdlib]
    - import numpy as np                             [third-party]
  Line count: 70
  __all__: (none)
```

```
FILE: prediction_guards/policies.py
  Classes:
    - NonNegativePredictionMixin
        Methods: _postprocess_predictions(self, predictions: np.ndarray) -> np.ndarray
  Functions: (none)
  Imports:
    - import numpy as np                             [third-party]
  Line count: 15
  __all__: (none)
```

```
FILE: prediction_guards/submission.py
  Classes: (none)
  Functions:
    - is_valid_score(score: float) -> bool
    - validate_go_term_format(term: str) -> Tuple[bool, Optional[str]]
    - validate_submission_format(filepath: str, sample_size: int = 1000) -> Tuple[bool, List[str]]
  Imports:
    - import re                                      [stdlib]
    - from pathlib import Path                       [stdlib]
    - from typing import List, Optional, Tuple       [stdlib]
  Line count: 117
  __all__: (none)
```

```
FILE: prediction_guards/verify_export_files.py
  Classes: (none)
  Functions:
    - _make_result(success: bool, message: str, model_path: Optional[Path]) -> Dict[str, Union[bool, str, Optional[Path]]]
    - verify_export_files(export_dir: Union[str, Path], model_type: str = 'end_to_end') -> Dict[str, Union[bool, str, Optional[Path]]]
  Imports:
    - from pathlib import Path                       [stdlib]
    - from typing import Union, Dict, Optional       [stdlib]
  Line count: 57
  __all__: (none)
```

```
FILE: protein_features/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .amino_acid_constants import AA_WEIGHTS, HYDROPATHY_VALUES, AA_ALPHABET, AA_GROUPS, TOP_DIPEPTIDES, TOP_TRIPEPTIDES, HANDCRAFTED_FEATURE_DIM  [internal]
    - from .kmer_features import extract_kmer_frequencies  [internal]
  Line count: 20
  __all__: ['AA_WEIGHTS', 'HYDROPATHY_VALUES', 'AA_ALPHABET', 'AA_GROUPS', 'TOP_DIPEPTIDES', 'TOP_TRIPEPTIDES', 'HANDCRAFTED_FEATURE_DIM', 'extract_kmer_frequencies']
```

```
FILE: protein_features/amino_acid_constants.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from typing import Dict, Set                   [stdlib]
  Line count: 57
  __all__: (none)
  Module-level: AA_WEIGHTS, HYDROPATHY_VALUES, AA_ALPHABET, AA_GROUPS, TOP_DIPEPTIDES, TOP_TRIPEPTIDES, HANDCRAFTED_FEATURE_DIM
```

```
FILE: protein_features/kmer_features.py
  Classes: (none)
  Functions:
    - extract_kmer_frequencies(seq: str, k: int = 2) -> Dict[str, float]
  Imports:
    - from collections import Counter                [stdlib]
    - from typing import Dict                        [stdlib]
  Line count: 34
  __all__: (none)
```

```
FILE: runtime/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .base_command_builder import BaseCommandBuilder  [internal]
    - from .cache_paths import DerivedCachePaths, derive_cache_paths  [internal]
    - from .execution_result import ExecutionResult  [internal]
    - from .environment_setup import setup_environment  [internal]
    - from .log_configure import get_logger, reset_logging, setup_logging, get_isolated_logger  [internal]
    - from .platform_detection import is_kaggle, is_kaggle_input  [internal]
    - from .run_command_stream import run_command_stream, validate_command  [internal]
    - from .runtime_types import ProcessResult, DeviceInfo  [internal]
    - from .torch_guard import TorchAbsentModule, get_nn_module_base_class, get_torch, get_vision_module_and_tensor_types, is_torch_available  [internal]
  Line count: 41
  __all__: ['BaseCommandBuilder', 'DerivedCachePaths', 'derive_cache_paths', 'ExecutionResult', 'get_logger', 'reset_logging', 'setup_environment', 'setup_logging', 'get_isolated_logger', 'is_kaggle', 'is_kaggle_input', 'run_command_stream', 'validate_command', 'ProcessResult', 'DeviceInfo', 'TorchAbsentModule', 'get_nn_module_base_class', 'get_torch', 'get_vision_module_and_tensor_types', 'is_torch_available']
```

```
FILE: runtime/base_command_builder.py
  Classes:
    - BaseCommandBuilder
        Methods: __init__(self, base_executable: Optional[List[str]] = None)
                 build(self) -> List[str]
                 add_positional(self, value: Any) -> None
                 add_flag(self, flag: str, condition: bool) -> None
                 add_option(self, flag: str, value: Optional[Any]) -> None
                 add_list_option(self, flag: str, values: Optional[List[Any]]) -> None
  Functions: (none)
  Imports:
    - from typing import List, Optional, Any         [stdlib]
  Line count: 64
  __all__: (none)
```

```
FILE: runtime/cache_paths.py
  Classes:
    - DerivedCachePaths  [dataclass]
        Fields: feature_cache_dir: str, model_cache_dir: str
  Functions:
    - derive_cache_paths(cache_dir: Union[str, Path], feature_cache_dir: Optional[Union[str, Path]] = None, model_cache_dir: Optional[Union[str, Path]] = None) -> DerivedCachePaths
  Imports:
    - from pathlib import Path                       [stdlib]
    - from dataclasses import dataclass              [stdlib]
    - from typing import Optional, Union             [stdlib]
  Line count: 27
  __all__: (none)
```

```
FILE: runtime/environment_setup.py
  Classes: (none)
  Functions:
    - setup_environment(model_name: Optional[str] = None, download_weights: bool = True) -> None
  Imports:
    - from typing import Optional                    [stdlib]
  Line count: 15
  __all__: (none)
```

```
FILE: runtime/execution_result.py
  Classes:
    - ExecutionResult  [frozen dataclass]
        Fields: returncode: int, output: Sequence[str], log_file: str | None
        Methods (properties): succeeded(self) -> bool, failed(self) -> bool
  Functions: (none)
  Imports:
    - from dataclasses import dataclass              [stdlib]
    - from typing import Sequence                    [stdlib]
  Line count: 21
  __all__: (none)
```

```
FILE: runtime/log_configure.py
  Classes: (none)
  Functions:
    - setup_logging(level: Optional[str] = None) -> None
    - get_logger(name: str, level: int = logging.INFO) -> logging.Logger
    - reset_logging() -> None
    - get_isolated_logger(name: str, level: int = logging.INFO, namespace: Optional[str] = None) -> logging.Logger
  Imports:
    - import os                                      [stdlib]
    - import sys                                     [stdlib]
    - import logging                                 [stdlib]
    - from typing import Optional                    [stdlib]
  Line count: 89
  __all__: (none)
```

```
FILE: runtime/platform_detection.py
  Classes: (none)
  Functions:
    - is_kaggle() -> bool
    - is_kaggle_input(path: Union[Path, str]) -> bool
  Imports:
    - import os                                      [stdlib]
    - from pathlib import Path                       [stdlib]
    - from typing import Union                       [stdlib]
  Line count: 15
  __all__: (none)
```

```
FILE: runtime/run_command_stream.py
  Classes: (none)
  Functions:
    - validate_command(cmd: List[str]) -> None
    - run_command_stream(cmd: List[str], timeout: Optional[int] = None, keep_last_n: int = 200) -> Tuple[int, List[str]]
  Imports:
    - import subprocess                              [stdlib]
    - from collections import deque                  [stdlib]
    - from typing import List, Optional, Tuple       [stdlib]
  Line count: 55
  __all__: (none)
```

```
FILE: runtime/runtime_types.py
  Classes:
    - ProcessResult(TypedDict) — keys: returncode, stdout, stderr
    - DeviceInfo(TypedDict) — keys: cuda_available, device_count, device_names
  Functions: (none)
  Imports:
    - from typing import TypedDict, List            [stdlib]
  Line count: 17
  __all__: (none)
```

```
FILE: runtime/torch_guard.py
  Classes:
    - TorchAbsentModule
        Methods: __init__(self) -> None
  Functions:
    - _load_torch()  [lru_cache — imports torch inside try]
    - get_torch()
    - is_torch_available() -> bool
    - get_nn_module_base_class()
    - get_vision_module_and_tensor_types() -> tuple[Any, Any]
  Imports (module level):
    - import functools                               [stdlib]
    - from typing import Any                         [stdlib]
  Imports (function-local): import torch inside _load_torch
  Line count: 54
  __all__: (none)
```

```
FILE: scoring/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .calculate_percentile_weights import calculate_percentile_weights  [internal]
    - from .combine_predictions import combine_predictions_loop, combine_predictions_vectorized  [internal]
    - from .ensemble_weights import combine_predictions_weighted_average, fit_stacking_weights_from_scores  [internal]
  Line count: 16
  __all__: ['calculate_percentile_weights', 'combine_predictions_loop', 'combine_predictions_vectorized', 'combine_predictions_weighted_average', 'fit_stacking_weights_from_scores']
```

```
FILE: scoring/calculate_percentile_weights.py
  Classes: (none)
  Functions:
    - calculate_percentile_weights(scores: np.ndarray) -> np.ndarray
  Imports:
    - import numpy as np                             [third-party]
    - from scipy.stats import rankdata               [third-party]
  Line count: 24
  __all__: (none)
```

```
FILE: scoring/combine_predictions.py
  Classes: (none)
  Functions:
    - combine_predictions_loop(predictions_list: List[np.ndarray], weight_matrix: np.ndarray, result: np.ndarray) -> np.ndarray
    - combine_predictions_vectorized(predictions_list: List[np.ndarray], weight_matrix: np.ndarray) -> np.ndarray
  Imports:
    - import numpy as np                             [third-party]
    - from typing import List                        [stdlib]
  Line count: 54
  __all__: (none)
```

```
FILE: scoring/ensemble_weights.py
  Classes: (none)
  Functions:
    - combine_predictions_weighted_average(predictions_list: List[Dict[str, np.ndarray]], weights: Optional[List[float]] = None) -> Dict[str, np.ndarray]
    - fit_stacking_weights_from_scores(scores: np.ndarray, temperature: float = 2.0) -> np.ndarray
  Imports:
    - import numpy as np                             [third-party]
    - from typing import Dict, List, Optional        [stdlib]
  Line count: 79
  __all__: (none)
```

```
FILE: training/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .build_config import build_training_config  [internal]
    - from .epoch_history import create_history_entry  [internal]
    - from .extract_batch_data import extract_batch_data  [internal]
    - from .scheduler import get_scheduler_mode, step_scheduler  [internal]
  Line count: 14
  __all__: ['build_training_config', 'create_history_entry', 'extract_batch_data', 'get_scheduler_mode', 'step_scheduler']
```

```
FILE: training/build_config.py
  Classes: (none)
  Functions:
    - build_training_config(batch_size: int, num_epochs: int, learning_rate: float, optimizer: str, loss_function: str, scheduler: str, **extra: Any) -> Dict[str, Any]
  Imports:
    - from typing import Any, Dict                   [stdlib]
  Line count: 42
  __all__: (none)
```

```
FILE: training/epoch_history.py
  Classes: (none)
  Functions:
    - create_history_entry(*, epoch: int, train_loss: float, val_loss: float, primary_metric_name: str, primary_metric_value: float, optimizer: Optional[Any], per_target_scores: Optional[np.ndarray] = None) -> Dict[str, Any]
  Imports:
    - import numpy as np                             [third-party]
    - from typing import Any, Dict, Optional       [stdlib]
  Line count: 55
  __all__: (none)
```

```
FILE: training/extract_batch_data.py
  Classes: (none)
  Functions:
    - extract_batch_data(batch: Union[Any, Tuple, list], device: Any) -> Tuple[Any, Optional[Any]]
  Imports:
    - from typing import Tuple, Optional, Union, Any  [stdlib]
  Line count: 35
  __all__: (none)
```

```
FILE: training/scheduler.py
  Classes: (none)
  Functions:
    - get_scheduler_mode(config: Any) -> str
    - step_scheduler(scheduler: Optional[Any], config: Any, primary_metric_value: float, val_loss: float) -> None
  Imports:
    - from typing import Any, Optional               [stdlib]
  Line count: 58
  __all__: (none)
```

```
FILE: vision/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .image import get_image_size_from_config, load_image_pil, load_image_rgb, split_image  [internal]
    - from .minimal_val_transform import IMAGENET_MEAN, IMAGENET_STD, build_minimal_val_transform  [internal]
    - from .model_path import is_huggingface_model_path  [internal]
    - from .model_type import detect_vision_model_type  [internal]
    - from .noise_reduction import noise_reduction  [internal]
    - from .transform_constants import DEFAULT_PREPROCESSING_LIST, AVAILABLE_PREPROCESSING, AVAILABLE_AUGMENTATION, AVAILABLE_TTA_VARIANTS, DEFAULT_TTA_VARIANTS  [internal]
    - from .transform_defaults import DEFAULT_BLUR_KERNEL_SIZE, DEFAULT_BLUR_SIGMA, DEFAULT_COLOR_BRIGHTNESS, DEFAULT_COLOR_CONTRAST, DEFAULT_COLOR_SATURATION, DEFAULT_COLOR_HUE, DEFAULT_GEOMETRIC_DEGREES, DEFAULT_GEOMETRIC_TRANSLATE, DEFAULT_GEOMETRIC_SCALE, DEFAULT_GEOMETRIC_SHEAR, DEFAULT_NOISE_MEAN, DEFAULT_NOISE_STD, DEFAULT_NOISE_REDUCTION_KERNEL_SIZE, DEFAULT_NOISE_REDUCTION_METHOD, DEFAULT_CONTRAST_ENHANCEMENT_METHOD  [internal]
    - from .transform_mode import TransformMode      [internal]
  Line count: 66
  __all__: ['get_image_size_from_config', 'load_image_pil', 'load_image_rgb', 'split_image', 'IMAGENET_MEAN', 'IMAGENET_STD', 'build_minimal_val_transform', 'is_huggingface_model_path', 'detect_vision_model_type', 'noise_reduction', 'DEFAULT_PREPROCESSING_LIST', 'AVAILABLE_PREPROCESSING', 'AVAILABLE_AUGMENTATION', 'AVAILABLE_TTA_VARIANTS', 'DEFAULT_TTA_VARIANTS', 'DEFAULT_BLUR_KERNEL_SIZE', 'DEFAULT_BLUR_SIGMA', 'DEFAULT_COLOR_BRIGHTNESS', 'DEFAULT_COLOR_CONTRAST', 'DEFAULT_COLOR_SATURATION', 'DEFAULT_COLOR_HUE', 'DEFAULT_GEOMETRIC_DEGREES', 'DEFAULT_GEOMETRIC_TRANSLATE', 'DEFAULT_GEOMETRIC_SCALE', 'DEFAULT_GEOMETRIC_SHEAR', 'DEFAULT_NOISE_MEAN', 'DEFAULT_NOISE_STD', 'DEFAULT_NOISE_REDUCTION_KERNEL_SIZE', 'DEFAULT_NOISE_REDUCTION_METHOD', 'DEFAULT_CONTRAST_ENHANCEMENT_METHOD', 'TransformMode']
```

```
FILE: vision/image/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .config import get_image_size_from_config  [internal]
    - from .loading import load_image_pil, load_image_rgb  [internal]
    - from .patching import split_image               [internal]
  Line count: 12
  __all__: ['get_image_size_from_config', 'load_image_pil', 'load_image_rgb', 'split_image']
```

```
FILE: vision/image/config.py
  Classes: (none)
  Functions:
    - get_image_size_from_config(config: Any) -> Optional[Union[int, Tuple[int, int]]]
  Imports:
    - from typing import Any, Optional, Tuple, Union  [stdlib]
  Line count: 24
  __all__: (none)
```

```
FILE: vision/image/loading.py
  Classes: (none)
  Functions:
    - load_image_pil(path: Path, convert_rgb: bool = True) -> Image.Image
    - load_image_rgb(image: Union[np.ndarray, Image.Image, str, Path]) -> np.ndarray
  Imports:
    - import cv2                                     [third-party]
    - import numpy as np                             [third-party]
    - from PIL import Image                          [third-party]
    - from pathlib import Path                       [stdlib]
    - from typing import Union                       [stdlib]
  Line count: 52
  __all__: (none)
```

```
FILE: vision/image/patching.py
  Classes: (none)
  Functions:
    - split_image(image: np.ndarray, patch_size: int = 520, overlap: int = 16) -> List[np.ndarray]
  Imports:
    - import numpy as np                             [third-party]
    - from typing import List                        [stdlib]
  Line count: 38
  __all__: (none)
```

```
FILE: vision/minimal_val_transform.py
  Classes: (none)
  Functions:
    - build_minimal_val_transform(image_size: Tuple[int, int])  [returns Compose; requires torchvision at runtime]
  Imports (module level):
    - from typing import Tuple                       [stdlib]
  Imports (function-local): from torchvision.transforms import Compose, Normalize, Resize, ToTensor
  Module-level: IMAGENET_MEAN, IMAGENET_STD (lists)
  Line count: 22
  __all__: (none)
```

```
FILE: vision/model_path.py
  Classes: (none)
  Functions:
    - is_huggingface_model_path(model: str) -> bool
  Imports:
    - from pathlib import Path                       [stdlib]
  Line count: 37
  __all__: (none)
```

```
FILE: vision/model_type.py
  Classes: (none)
  Functions:
    - detect_vision_model_type(model: str, *, dinov2_policy: Optional[Callable[[str], bool]] = None) -> str
  Imports:
    - from typing import Callable, Optional          [stdlib]
  Line count: 42
  __all__: (none)
```

```
FILE: vision/noise_reduction.py
  Classes: (none)
  Functions:
    - noise_reduction(image: Union[Image.Image, np.ndarray], method: str = 'gaussian_blur', kernel_size: int = 5) -> Union[Image.Image, np.ndarray]
  Imports:
    - import numpy as np                             [third-party]
    - import cv2                                     [third-party]
    - from PIL import Image                          [third-party]
    - from typing import Union                       [stdlib]
  Line count: 62
  __all__: (none)
```

```
FILE: vision/transform_constants.py
  Classes: (none)
  Functions: (none)
  Imports: (none)
  Line count: 42
  __all__: (none)
  Module-level: DEFAULT_PREPROCESSING_LIST, AVAILABLE_PREPROCESSING, AVAILABLE_AUGMENTATION, AVAILABLE_TTA_VARIANTS, DEFAULT_TTA_VARIANTS
```

```
FILE: vision/transform_defaults.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from typing import Tuple                       [stdlib]
  Line count: 28
  __all__: (none)
  Module-level: DEFAULT_BLUR_KERNEL_SIZE, DEFAULT_BLUR_SIGMA, DEFAULT_COLOR_*, DEFAULT_GEOMETRIC_*, DEFAULT_NOISE_*, DEFAULT_NOISE_REDUCTION_*, DEFAULT_CONTRAST_ENHANCEMENT_METHOD
```

```
FILE: vision/transform_mode.py
  Classes:
    - TransformMode(Enum)
        Members: TRAIN, VAL, TEST, TTA
  Functions: (none)
  Imports:
    - from enum import Enum                          [stdlib]
  Line count: 18
  __all__: (none)
```

## 3. __init__.py Public API Summary

```
INIT: __init__.py
  Exports: concatenation of all subpackage __all__ symbols (abstractions, cli, config, embeddings, errors, grid_search, ontology, paths, prediction_guards, protein_features, runtime, scoring, training, vision)
  Re-exports from: (star-import re-export from each subpackage listed in §2 root file)
```

```
INIT: abstractions/__init__.py
  Exports: EnsemblingMethod, GridSearchContext, HandlerContextBuilder, Metric, ModelRegistry, NamedRegistry, build_unknown_key_error, PipelineResult
  Re-exports from: abstractions/*.py modules
```

```
INIT: cli/__init__.py
  Exports: get_arg, parse_comma_separated, comma_separated_type, parse_key_value_pairs, add_model_type_argument, add_model_path_argument, add_ensemble_method_argument, Command, add_common_arguments, dispatch_command
  Re-exports from: cli/args_utils, argument_groups, commands, common_args, dispatcher
```

```
INIT: config/__init__.py
  Exports: BaseConfig, TrainingSchema, EvaluationSchema, PathConfig, CompositeConfig, get_config_value, DataSplit, PipelineConfig, RuntimeConfig, TrainingCadenceConfig, TrainingMode
  Re-exports from: config/* modules
```

```
INIT: embeddings/__init__.py
  Exports: align_embeddings, find_common_ids, normalize_embedding_type, resolve_embedding_base_path
  Re-exports from: embeddings/* modules
```

```
INIT: errors/__init__.py
  Exports: full exception surface (19 symbols — Config*, Data*, Model*, Pipeline*, CoreRuntimeError, DeviceError, EnvironmentConfigError, ProcessError, ExecutionError)
  Re-exports from: errors/*_errors modules
```

```
INIT: grid_search/__init__.py
  Exports: constants, grid/param helpers, result builders/selection, varied_params, combinatorics (35 names — see §2)
  Re-exports from: grid_search/* modules
```

```
INIT: ontology/__init__.py
  Exports: parse_obo_file
  Re-exports from: ontology/obo_parser
```

```
INIT: paths/__init__.py
  Exports: ensure_dir, normalize_path, get_file_size_mb, ensure_file_dir, get_fold_checkpoint_path, get_fold_regression_model_path
  Re-exports from: paths/filesystem, fold_paths
```

```
INIT: prediction_guards/__init__.py
  Exports: validation helpers, NonNegativePredictionMixin, submission validators, verify_export_files
  Re-exports from: prediction_guards/* modules
```

```
INIT: protein_features/__init__.py
  Exports: AA_WEIGHTS, HYDROPATHY_VALUES, AA_ALPHABET, AA_GROUPS, TOP_DIPEPTIDES, TOP_TRIPEPTIDES, HANDCRAFTED_FEATURE_DIM, extract_kmer_frequencies
  Re-exports from: protein_features/amino_acid_constants, kmer_features
```

```
INIT: runtime/__init__.py
  Exports: BaseCommandBuilder, DerivedCachePaths, derive_cache_paths, ExecutionResult, logging helpers, platform detection, run_command_stream/validate_command, ProcessResult, DeviceInfo, torch_guard symbols
  Re-exports from: runtime/* modules
```

```
INIT: scoring/__init__.py
  Exports: calculate_percentile_weights, combine_predictions_loop, combine_predictions_vectorized, combine_predictions_weighted_average, fit_stacking_weights_from_scores
  Re-exports from: scoring/* modules
```

```
INIT: training/__init__.py
  Exports: build_training_config, create_history_entry, extract_batch_data, get_scheduler_mode, step_scheduler
  Re-exports from: training/* modules
```

```
INIT: vision/__init__.py
  Exports: image IO/patch helpers, Imagenet constants, build_minimal_val_transform, model path/type, noise_reduction, transform constants/defaults, TransformMode
  Re-exports from: vision/* and vision/image/*
```

```
INIT: vision/image/__init__.py
  Exports: get_image_size_from_config, load_image_pil, load_image_rgb, split_image
  Re-exports from: vision/image/config, loading, patching
```

## 4. Import Dependency Map

```
INTERNAL IMPORTS SUMMARY:
  From level_0 .. level_(N-1): N=0 — no lower numeric levels exist; not applicable.

  From same level (level_0):
    - All cross-module references use relative package imports (`from .…`, `from .subpackage import …`) under `scripts/layers/layer_0_core/level_0/`.
    - No `from level_0 import …` or `from level_0.xxx` patterns observed in `.py` logic files.
    - Root `__init__.py` uses star re-exports from subpackages (aggregation pattern).

  From level_(N+1) or higher (upward): none observed (no imports from `layer_1_core`, `level_1`, `layer_2`, etc.).

  Third-party / optional (not project-internal):
    - numpy, scipy.stats.rankdata, cv2, PIL.Image, obonet (optional, function-local in ontology/obo_parser), torch and torchvision (lazy/function-local in runtime/torch_guard, vision/minimal_val_transform).

  Stdlib: argparse, collections, dataclasses, enum, functools, itertools, logging, os, pathlib, re, subprocess, sys, typing, abc, and typing extensions (TypedDict, Protocol) as used above.
```

## 5. Flags

```
FLAGS:
  level_0/grid_search/result_selection.py — 131 lines (largest module in tier by line count; still under 300)
  level_0/prediction_guards/submission.py — 117 lines
  level_0/cli/args_utils.py — 96 lines
  level_0/paths/filesystem.py — 95 lines
  level_0/runtime/log_configure.py — 89 lines
  level_0/ontology/__init__.py — 5 lines (minimal package surface)
  level_0/cli/common_args.py — 8 lines
  level_0/config/training_modes.py — 10 lines
  level_0/vision/minimal_val_transform.py — optional torchvision; raises ModuleNotFoundError if missing when `build_minimal_val_transform` runs
  level_0/runtime/torch_guard.py — optional torch via cached import
  level_0/ontology/obo_parser.py — optional obonet; manual fallback if ImportError
  level_0/protein_features/amino_acid_constants.py — long comment block documenting HANDCRAFTED_FEATURE_DIM vs CTD feature count (not a `legacy` keyword hit)
  level_0/errors/model_errors.py, pipeline_errors.py — docstrings mention “Incompatible” (substring `compat`); not marked as deprecation shims
  Duplicate simple names across protocols: `get_paths`, `get_config` appear on both GridSearchContext and HandlerContextBuilder (distinct Protocol types)
  Root `__init__.py` — very wide star-export surface (aggregator barrel for entire tier)
```

## 6. Static scan summary

```
Precheck (machine): see c:\Users\mdc0431\OneDrive - UNT System\Documents\Kaggle\code\input\kaggle-ml-comp-scripts\.cursor\audit-results\general\summaries\precheck_level_0_2026-04-08.md
  - precheck_status: skipped_machine_script
  - Reason: ModuleNotFoundError: No module named 'torchvision' in the environment running `audit_precheck.py`
  - Effect: Phase 7 machine reconciliation / full devtools precheck stack could not run; inventory here is tree + source derived only.
```
