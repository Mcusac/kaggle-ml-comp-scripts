---
generated: 2026-04-08
audit_scope: competition_infra
level_name: level_1
pass_number: 1
run_id: comp_infra_overhaul_2026-04-08
artifact_kind: inventory
audit_profile: full
---

# INVENTORY: level_1

## 1. Package & File Tree

```
level_1/  (README: yes)
  __init__.py
  contest/  (README: yes)
    __init__.py
    argparse_builders.py
    cli.py
    context.py
    csv_io.py
    data_loading.py
    splits.py
  export/  (README: yes)
    __init__.py
    export_model_pipeline.py
    feature_filename.py
    metadata_builders.py
    source_handlers.py
  features/  (README: yes)
    __init__.py
    feature_extractor_factory.py
  grid_search/  (README: yes)
    __init__.py
    base.py
    context.py
    context_types.py
    handlers/  (README: yes)
    __init__.py
    command_handlers.py
    handler_context.py
    commands/  (README: yes)
      __init__.py
      cross_validate.py
      ensemble.py
      export_model.py
      grid_search.py
      test.py
      train.py
      train_test.py
  notebook/  (README: yes)
    __init__.py
    base_commands.py
    dispatch.py
    streaming.py
  paths/  (README: yes)
    __init__.py
    env_paths.py
    models.py
    output_roots.py
    path_utils.py
    runs.py
    submissions.py
  pipelines/  (README: yes)
    __init__.py
    validate_train_submit.py
  registry/  (README: yes)
    __init__.py
    contest_registry.py
```

Note: `contest/__init__.py` re-exports validate-first pipeline shells from `layers.layer_0_core.level_1.pipelines` (no local `pipeline_shells.py`).

---

## 2. Per-File Details

```
FILE: level_1/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from . import contest, export, features, grid_search, handlers, notebook, paths, pipelines, registry  [internal / aggregation]
    - from .contest import *  [internal]
    - from .export import *  [internal]
    - from .features import *  [internal]
    - from .grid_search import *  [internal]
    - from .handlers import *  [internal]
    - from .notebook import *  [internal]
    - from .paths import *  [internal]
    - from .pipelines import *  [internal]
    - from .registry import *  [internal]
  Line count: 35
  __all__: tuple expression — list(contest.__all__) + list(export.__all__) + list(features.__all__) + list(grid_search.__all__) + list(handlers.__all__) + list(notebook.__all__) + list(paths.__all__) + list(pipelines.__all__) + list(registry.__all__)
```

```
FILE: level_1/contest/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .cli import add_common_contest_args, parse_models_csv, parse_optional_float_list, parse_weights_csv, resolve_data_root_from_args, resolve_handler_args  [internal]
    - from .context import ContestContext, build_contest_context  [internal]
    - from .csv_io import load_training_csv  [internal]
    - from .splits import split_train_val  [internal]
    - from .data_loading import load_contest_data, load_contest_training_data  [internal]
    - from .argparse_builders import add_ensemble_weights_arg, add_max_targets_arg, add_models_arg, add_output_csv_arg, add_strategy_arg, add_train_mode_arg, add_validation_stacking_toggle  [internal]
    - from layers.layer_0_core.level_1.pipelines import BasePipeline, TwoStageValidateFirstPipelineResultShell, ValidateFirstPipelineResultShell, ValidateFirstRunner  [core re-export]
  Line count: 55
  __all__: ["add_common_contest_args", "build_contest_context", "ContestContext", "load_contest_data", "load_contest_training_data", "load_training_csv", "parse_models_csv", "parse_optional_float_list", "parse_weights_csv", "resolve_data_root_from_args", "resolve_handler_args", "split_train_val", "add_ensemble_weights_arg", "add_max_targets_arg", "add_models_arg", "add_output_csv_arg", "add_strategy_arg", "add_train_mode_arg", "add_validation_stacking_toggle", "BasePipeline", "ValidateFirstRunner", "ValidateFirstPipelineResultShell", "TwoStageValidateFirstPipelineResultShell"]
```

```
FILE: level_1/contest/argparse_builders.py
  Classes: (none)
  Functions:
    - add_train_mode_arg(parser: argparse.ArgumentParser, *, default: str = "end_to_end", help_text: Optional[str] = "Training pipeline label (e.g. end_to_end, multi_part)") -> None
    - add_models_arg(parser: argparse.ArgumentParser, *, default: str = "baseline_approx", help_text: Optional[str] = "Comma-separated model names (e.g. baseline_approx)") -> None
    - add_max_targets_arg(parser: argparse.ArgumentParser, *, default: int = 0, help_text: Optional[str] = "If >0, only use the first N targets") -> None
    - add_output_csv_arg(parser: argparse.ArgumentParser, *, help_text: Optional[str] = "Optional output CSV path") -> None
    - add_strategy_arg(parser: argparse.ArgumentParser, *, choices: Iterable[str] = ("single", "ensemble", "stacking", "stacking_ensemble"), default: str = "single", help_text: Optional[str] = "Submission strategy") -> None
    - add_ensemble_weights_arg(parser: argparse.ArgumentParser, *, help_text: Optional[str] = "Comma-separated weights for ensemble/stacking") -> None
    - add_validation_stacking_toggle(parser: argparse.ArgumentParser, *, default: bool = True, flag_name: str = "--no-validation-stacking", dest: str = "use_validation_for_stacking", help_text: Optional[str] = None) -> None
  Imports:
    - import argparse  [stdlib]
    - from typing import Iterable, Optional  [stdlib]
  Line count: 112
  __all__: ["add_ensemble_weights_arg", "add_max_targets_arg", "add_models_arg", "add_output_csv_arg", "add_strategy_arg", "add_train_mode_arg", "add_validation_stacking_toggle"]
```

```
FILE: level_1/contest/cli.py
  Classes: (none)
  Functions:
    - resolve_handler_args(args: Any, defaults: Dict[str, Any]) -> Dict[str, Any]
    - add_common_contest_args(parser: argparse.ArgumentParser) -> None
    - resolve_data_root_from_args(args: Any) -> str
    - parse_models_csv(raw: Optional[str], *, default: Optional[List[str]] = None) -> List[str]
    - parse_optional_float_list(raw: Optional[str]) -> Optional[List[float]]
    - parse_weights_csv(raw: Optional[str]) -> Optional[List[float]]
  Imports:
    - import argparse  [stdlib]
    - from typing import Any, Dict, List, Optional  [stdlib]
    - from layers.layer_1_competition.level_0_infra.level_1.paths import get_data_root_path  [internal — level_1.paths]
  Line count: 73
  __all__: (none)
```

```
FILE: level_1/contest/context.py
  Classes:
    - ContestContext
        Methods:
                 local_data_root(self) -> str  (@property)
                 get_paths(self) -> Any
                 get_config(self) -> Any
                 get_data_schema(self) -> Any
                 get_post_processor(self) -> Any
  Functions:
    - build_contest_context(contest_name: str) -> ContestContext
  Imports:
    - from dataclasses import dataclass  [stdlib]
    - from typing import Any  [stdlib]
    - from layers.layer_1_competition.level_0_infra.level_1.registry import get_contest  [internal — level_1.registry]
  Line count: 65
  __all__: (none)
```

```
FILE: level_1/contest/csv_io.py
  Classes: (none)
  Functions:
    - load_training_csv(*, contest_entry: dict, train_csv_path: Path) -> pd.DataFrame
  Imports:
    - import pandas as pd  [third-party]
    - from pathlib import Path  [stdlib]
    - from layers.layer_0_core.level_0 import get_logger  [internal — layer_0_core]
    - from layers.layer_0_core.level_4 import load_csv_raw  [internal — layer_0_core]
  Line count: 20
  __all__: (none)
```

```
FILE: level_1/contest/data_loading.py
  Classes: (none)
  Functions:
    - load_contest_training_data(contest_name: str, train_csv_path: Path, validation_split: Optional[float] = None, n_folds: Optional[int] = None, fold: Optional[int] = None) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]
    - load_contest_data(contest_name: str, model_type: str, validation_split: Optional[float] = None, n_folds: Optional[int] = None, fold: Optional[int] = None) -> tuple
  Imports:
    - import pandas as pd  [third-party]
    - from typing import Optional, Tuple  [stdlib]
    - from pathlib import Path  [stdlib]
    - from layers.layer_0_core.level_0 import get_logger  [internal — layer_0_core]
    - from layers.layer_0_core.level_4 import load_csv_raw, load_csv_raw_if_exists  [internal — layer_0_core]
    - from layers.layer_1_competition.level_0_infra.level_1.contest.csv_io import load_training_csv  [internal — submodule to avoid package cycle]
    - from layers.layer_1_competition.level_0_infra.level_1.contest.splits import split_train_val  [internal]
    - from layers.layer_1_competition.level_0_infra.level_1.registry import ContestRegistry, get_contest  [internal]
  Line count: 107
  __all__: (none)
```

```
FILE: level_1/contest/splits.py
  Classes: (none)
  Functions:
    - split_train_val(*, train_data: pd.DataFrame, validation_split: Optional[float], n_folds: Optional[int], fold: Optional[int]) -> Tuple[pd.DataFrame, Optional[pd.DataFrame]]
  Imports:
    - from typing import Optional, Tuple  [stdlib]
    - import pandas as pd  [third-party]
    - from sklearn.model_selection import train_test_split  [third-party]
    - from layers.layer_0_core.level_1 import create_kfold_splits, get_fold_data  [internal — layer_0_core]
  Line count: 27
  __all__: (none)
```

```
FILE: level_1/export/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .metadata_builders import prepare_regression_model_metadata_dict  [internal]
    - from .source_handlers import handle_best_variant_file, handle_just_trained_model, handle_results_file  [internal]
    - from .export_model_pipeline import export_model_pipeline  [internal]
  Line count: 17
  __all__: ["export_model_pipeline", "prepare_regression_model_metadata_dict", "handle_best_variant_file", "handle_just_trained_model", "handle_results_file"]
```

```
FILE: level_1/export/export_model_pipeline.py
  Classes: (none)
  Functions:
    - export_model_pipeline(contest_context: Any, data_root: Optional[str] = None, results_file: Optional[str] = None, variant_id: Optional[str] = None, best_variant_file: Optional[str] = None, export_dir: Optional[str] = None, model_dir: Optional[str] = None, **kwargs) -> str
  Imports:
    - from pathlib import Path  [stdlib]
    - from typing import Optional, Any  [stdlib]
    - from layers.layer_0_core.level_0 import ensure_dir, get_logger  [internal — layer_0_core]
    - from layers.layer_1_competition.level_0_infra.level_1.export.source_handlers import handle_best_variant_file, handle_just_trained_model, handle_results_file  [internal — level_1.export]
  Line count: 73
  __all__: (none)
```

```
FILE: level_1/export/feature_filename.py
  Classes: (none)
  Functions:
    - resolve_feature_extraction_model_name(config: Any) -> Optional[str]
    - construct_feature_filename_from_config(config: Any) -> Optional[str]
  Imports:
    - from typing import Any, Optional  [stdlib]
    - from layers.layer_0_core.level_0 import get_logger  [internal — layer_0_core]
    - from layers.layer_0_core.level_1 import generate_feature_filename, get_model_id  [internal — layer_0_core]
    - from layers.layer_1_competition.level_0_infra.level_0 import get_model_name_from_pretrained  [internal — level_0_infra.level_0]
    - from layers.layer_0_core.level_6 import find_combo_id_from_config  [internal — layer_0_core]
  Line count: 43
  __all__: (none)
```

```
FILE: level_1/export/metadata_builders.py
  Classes: (none)
  Functions:
    - prepare_regression_model_metadata_dict(regression_model_type: str, cv_score: float, fold_scores: list[float], hyperparameters: Dict[str, Any], feature_filename: str, variant_id: str, variant_index: int, best_fold: Optional[int] = None, best_fold_score: Optional[float] = None) -> Dict[str, Any]
    - build_regression_metadata(config: Any, model_path: Path, best_fold: Optional[int], variant_id: Optional[str], variant_info: Optional[Dict[str, Any]]) -> Dict[str, Any]
    - build_end_to_end_metadata(config: Any, model_path: Path, best_fold: Optional[int], variant_id: Optional[str], variant_info: Optional[Dict[str, Any]]) -> Dict[str, Any]
  Imports:
    - from pathlib import Path  [stdlib]
    - from typing import Any, Dict, Optional  [stdlib]
    - from layers.layer_0_core.level_0 import ConfigValidationError, get_logger  [internal — layer_0_core]
    - from layers.layer_1_competition.level_0_infra.level_1.export.feature_filename import construct_feature_filename_from_config  [internal — level_1.export]
    - from layers.layer_0_core.level_5 import extract_scores_from_json, resolve_best_fold_and_score  [internal — layer_0_core]
  Line count: 135
  __all__: (none)
```

```
FILE: level_1/export/source_handlers.py
  Classes: (none)
  Functions:
    - handle_just_trained_model(model_dir: str, config: Any, variant_id: Optional[str] = None, variant_info: Optional[Dict[str, Any]] = None) -> Tuple[Path, Dict[str, Any]]
    - handle_best_variant_file(best_variant_file: str, config: Any, export_dir: Optional[str] = None, paths: Optional[Any] = None) -> Tuple[Path, Dict[str, Any]]
    - handle_results_file(results_file: str, variant_id: str, config: Any, export_dir: Optional[str] = None, paths: Optional[Any] = None) -> Tuple[Path, Dict[str, Any]]
    - _parse_results_csv(path: Path) -> list
  Imports:
    - import csv  [stdlib]
    - from pathlib import Path  [stdlib]
    - from typing import Any, Dict, Optional, Tuple  [stdlib]
    - from layers.layer_0_core.level_0 import get_logger  [internal — layer_0_core]
    - from layers.layer_0_core.level_4 import load_json_raw  [internal — layer_0_core]
    - from layers.layer_0_core.level_5 import find_trained_model_path  [internal — layer_0_core]
    - from layers.layer_1_competition.level_0_infra.level_1.export.metadata_builders import build_end_to_end_metadata, build_regression_metadata  [internal — level_1.export]
  Line count: 103
  __all__: (none)
```

```
FILE: level_1/features/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .feature_extractor_factory import create_feature_extraction_model, set_pretrained_weights_resolver  [internal]
  Line count: 8
  __all__: ("create_feature_extraction_model", "set_pretrained_weights_resolver")
```

```
FILE: level_1/features/feature_extractor_factory.py
  Classes: (none)
  Functions:
    - set_pretrained_weights_resolver(resolver: Optional[Callable[[str], str]]) -> None
    - create_feature_extraction_model(model_name: str, num_primary_targets: int, device: torch.device, image_size: Optional[Tuple[int, int]] = None, pretrained: bool = True) -> nn.Module
  Imports:
    - from typing import Optional, Tuple, Callable  [stdlib]
    - from layers.layer_0_core.level_0 import get_logger, get_torch  [internal — layer_0_core]
    - from layers.layer_0_core.level_3 import SigLIPExtractor  [internal — layer_0_core]
    - from layers.layer_0_core.level_4 import create_vision_model, SigLIPFeatureExtractorAdapter  [internal — layer_0_core]
    - from layers.layer_1_competition.level_0_infra.level_0 import get_pretrained_weights_path  [internal — level_0_infra.level_0]
  Line count: 79
  __all__: (none)
```

```
FILE: level_1/grid_search/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from layers.layer_0_core.level_4 import load_best_config_json  [internal — layer_0_core]
    - from .base import ContestGridSearchBase  [internal]
    - from .context import build_grid_search_context  [internal]
  Line count: 8
  __all__: ["ContestGridSearchBase", "load_best_config_json", "build_grid_search_context"]
```

```
FILE: level_1/grid_search/base.py
  Classes:
    - ContestGridSearchBase
        Methods:
                 __init__(self, config: Any, grid_search_type: str, contest_name: str, results_filename: str = "results.json", quick_mode: bool = False, **kwargs)
  Functions: (none)
  Imports:
    - from typing import Any  [stdlib]
    - from layers.layer_0_core.level_0 import get_logger  [internal — layer_0_core]
    - from layers.layer_0_core.level_6 import GridSearchBase  [internal — layer_0_core]
    - from layers.layer_1_competition.level_0_infra.level_1.registry import get_contest  [internal — level_1.registry]
  Line count: 69
  __all__: (none)
```

```
FILE: level_1/grid_search/context.py
  Classes: (none)
  Functions:
    - build_grid_search_context(contest_name: str, *, metric_calculator: Optional[Callable] = None, test_pipeline: Optional[Callable] = None, load_regression_gridsearch_results: Optional[Callable] = None, metadata_handler: Optional[Any] = None, parameter_grid_fn: Optional[Callable] = None, feature_cache_loader: Optional[Any] = None) -> Any
  Imports:
    - from typing import Any, Callable, Optional  [stdlib]
    - from layers.layer_1_competition.level_0_infra.level_1.registry import get_contest  [internal — level_1.registry]
    - from layers.layer_1_competition.level_0_infra.level_1.grid_search.context_types import ContestGridSearchContext  [internal — level_1.grid_search]
  Line count: 60
  __all__: (none)
```

```
FILE: level_1/grid_search/context_types.py
  Classes:
    - ContestGridSearchContext
        Methods:
                 __init__(self, *, paths: Any, config: Any, data_schema: Any, post_processor: Any, metric_calculator: Optional[Callable], test_pipeline: Optional[Callable], load_regression_gridsearch_results: Optional[Callable], metadata_handler: Optional[Any], parameter_grid_fn: Optional[Callable], feature_cache_loader: Optional[Any]) -> None
                 get_paths(self)
                 get_config(self)
                 get_metric_calculator(self)
                 get_data_schema(self)
                 get_post_processor(self)
                 get_test_pipeline(self)
                 load_regression_gridsearch_results(self, regression_model_type, variant_id=None, feature_filename=None)
                 get_metadata_handler(self)
                 get_feature_cache_loader(self)
                 get_parameter_grid_fn(self)
  Functions: (none)
  Imports:
    - from typing import Any, Callable, Optional  [stdlib]
  Line count: 71
  __all__: (none)
```

```
FILE: level_1/handlers/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .command_handlers import get_command_handlers  [internal]
  Line count: 5
  __all__: ["get_command_handlers"]
```

```
FILE: level_1/handlers/command_handlers.py
  Classes: (none)
  Functions:
    - get_command_handlers(builder: Any) -> Dict[str, Callable[[argparse.Namespace], None]]
  Imports:
    - import argparse  [stdlib]
    - from typing import Any, Callable, Dict  [stdlib]
    - from layers.layer_0_core.level_0 import Command  [internal — layer_0_core]
    - from layers.layer_1_competition.level_0_infra.level_1.handlers.commands.cross_validate import make_handler as make_cross_validate  [internal — level_1.handlers]
    - from layers.layer_1_competition.level_0_infra.level_1.handlers.commands.ensemble import make_handler as make_ensemble  [internal — level_1.handlers]
    - from layers.layer_1_competition.level_0_infra.level_1.handlers.commands.export_model import make_handler as make_export  [internal — level_1.handlers]
    - from layers.layer_1_competition.level_0_infra.level_1.handlers.commands.grid_search import make_handler as make_grid_search  [internal — level_1.handlers]
    - from layers.layer_1_competition.level_0_infra.level_1.handlers.commands.test import make_handler as make_test  [internal — level_1.handlers]
    - from layers.layer_1_competition.level_0_infra.level_1.handlers.commands.train import make_handler as make_train  [internal — level_1.handlers]
    - from layers.layer_1_competition.level_0_infra.level_1.handlers.commands.train_test import make_handler as make_train_test  [internal — level_1.handlers]
  Line count: 31
  __all__: (none)
```

```
FILE: level_1/handlers/commands/__init__.py
  Classes: (none)
  Functions: (none)
  Imports: (none)
  Line count: 4
  __all__: []
```

```
FILE: level_1/handlers/commands/cross_validate.py
  Classes: (none)
  Functions:
    - make_handler(builder: Any) -> Callable[[argparse.Namespace], None]
  Imports:
    - import argparse  [stdlib]
    - from typing import Any, Callable  [stdlib]
    - from layers.layer_0_core.level_0 import get_arg, get_logger  [internal — layer_0_core]
    - from layers.layer_0_core.level_9 import CrossValidateWorkflow  [internal — layer_0_core]
    - from layers.layer_1_competition.level_0_infra.level_0 import create_pipeline_kwargs  [internal — level_0_infra.level_0]
    - from layers.layer_1_competition.level_0_infra.level_1.handlers.handler_context import setup_handler_context  [internal — level_1.handlers]
  Line count: 31
  __all__: (none)
```

```
FILE: level_1/handlers/commands/ensemble.py
  Classes: (none)
  Functions:
    - make_handler(builder: Any) -> Callable[[argparse.Namespace], None]
  Imports:
    - import argparse  [stdlib]
    - from pathlib import Path  [stdlib]
    - from typing import Any, Callable  [stdlib]
    - import numpy as np  [third-party]
    - from layers.layer_0_core.level_0 import ensure_dir, get_arg, get_logger, parse_comma_separated  [internal — layer_0_core]
    - from layers.layer_0_core.level_2 import simple_average  [internal — layer_0_core]
  Line count: 48
  __all__: (none)
```

```
FILE: level_1/handlers/commands/export_model.py
  Classes: (none)
  Functions:
    - make_handler(builder: Any) -> Callable[[argparse.Namespace], None]
  Imports:
    - import argparse  [stdlib]
    - from typing import Any, Callable  [stdlib]
    - from layers.layer_0_core.level_0 import get_arg, get_logger  [internal — layer_0_core]
    - from layers.layer_0_core.level_5 import ExportPipeline  [internal — layer_0_core]
    - from layers.layer_1_competition.level_0_infra.level_1.handlers.handler_context import setup_handler_context  [internal — level_1.handlers]
  Line count: 27
  __all__: (none)
```

```
FILE: level_1/handlers/commands/grid_search.py
  Classes: (none)
  Functions:
    - make_handler(builder: Any) -> Callable[[argparse.Namespace], None]
  Imports:
    - import argparse  [stdlib]
    - from typing import Any, Callable  [stdlib]
    - from layers.layer_0_core.level_0 import get_logger  [internal — layer_0_core]
    - from layers.layer_0_core.level_9 import HyperparameterGridSearch  [internal — layer_0_core]
    - from layers.layer_1_competition.level_0_infra.level_1.handlers.handler_context import setup_handler_context  [internal — level_1.handlers]
  Line count: 27
  __all__: (none)
```

```
FILE: level_1/handlers/commands/test.py
  Classes: (none)
  Functions:
    - make_handler(builder: Any) -> Callable[[argparse.Namespace], None]
  Imports:
    - import argparse  [stdlib]
    - from typing import Any, Callable  [stdlib]
    - from layers.layer_0_core.level_0 import get_arg, get_logger  [internal — layer_0_core]
    - from layers.layer_0_core.level_6 import PredictPipeline  [internal — layer_0_core]
    - from layers.layer_1_competition.level_0_infra.level_0 import create_pipeline_kwargs  [internal — level_0_infra.level_0]
    - from layers.layer_1_competition.level_0_infra.level_1.handlers.handler_context import setup_handler_context  [internal — level_1.handlers]
  Line count: 36
  __all__: (none)
```

```
FILE: level_1/handlers/commands/train.py
  Classes: (none)
  Functions:
    - make_handler(builder: Any) -> Callable[[argparse.Namespace], None]
  Imports:
    - import argparse  [stdlib]
    - from typing import Any, Callable  [stdlib]
    - from layers.layer_0_core.level_0 import get_arg, get_logger  [internal — layer_0_core]
    - from layers.layer_0_core.level_8 import TrainPipeline  [internal — layer_0_core]
    - from layers.layer_1_competition.level_0_infra.level_0 import create_pipeline_kwargs  [internal — level_0_infra.level_0]
    - from layers.layer_1_competition.level_0_infra.level_1.handlers.handler_context import setup_handler_context  [internal — level_1.handlers]
  Line count: 31
  __all__: (none)
```

```
FILE: level_1/handlers/commands/train_test.py
  Classes: (none)
  Functions:
    - make_handler(builder: Any) -> Callable[[argparse.Namespace], None]
  Imports:
    - import argparse  [stdlib]
    - from typing import Any, Callable  [stdlib]
    - from layers.layer_0_core.level_0 import get_arg, get_logger  [internal — layer_0_core]
    - from layers.layer_0_core.level_9 import TrainPredictWorkflow  [internal — layer_0_core]
    - from layers.layer_1_competition.level_0_infra.level_0 import create_pipeline_kwargs  [internal — level_0_infra.level_0]
    - from layers.layer_1_competition.level_0_infra.level_1.handlers.handler_context import setup_handler_context  [internal — level_1.handlers]
  Line count: 39
  __all__: (none)
```

```
FILE: level_1/handlers/handler_context.py
  Classes: (none)
  Functions:
    - setup_handler_context(*, args: argparse.Namespace, builder: Any) -> tuple[str, Any, str, Any, Any, Any]
  Imports:
    - import argparse  [stdlib]
    - from typing import Any  [stdlib]
    - from layers.layer_0_core.level_0 import get_arg  [internal — layer_0_core]
  Line count: 24
  __all__: (none)
```

```
FILE: level_1/notebook/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .base_commands import build_run_py_base_command  [internal]
    - from .dispatch import get_notebook_commands_module, list_contests_with_notebook_commands, register_notebook_commands_module  [internal]
    - from .streaming import run_cli_streaming  [internal]
  Line count: 17
  __all__: ["build_run_py_base_command", "get_notebook_commands_module", "list_contests_with_notebook_commands", "register_notebook_commands_module", "run_cli_streaming"]
```

```
FILE: level_1/notebook/base_commands.py
  Classes: (none)
  Functions:
    - build_run_py_base_command(contest_name: str, subcommand: str, data_root: Optional[str] = None) -> List[str]
  Imports:
    - import sys  [stdlib]
    - from typing import List, Optional  [stdlib]
    - from layers.layer_1_competition.level_0_infra.level_1.paths import get_data_root_path, get_run_py_path  [internal — level_1.paths]
  Line count: 37
  __all__: (none)
```

```
FILE: level_1/notebook/dispatch.py
  Classes: (none)
  Functions:
    - list_contests_with_notebook_commands() -> List[str]
    - get_notebook_commands_module(contest: str) -> ModuleType
    - register_notebook_commands_module(contest: str, module_path: str) -> None
  Imports:
    - import importlib  [stdlib]
    - from types import ModuleType  [stdlib]
    - from typing import Dict, List  [stdlib]
  Line count: 52
  __all__: (none)
```

```
FILE: level_1/notebook/streaming.py
  Classes: (none)
  Functions:
    - run_cli_streaming(cmd: List[str], *, description: Optional[str] = None, keep_last_n: int = 200) -> Tuple[int, List[str]]
  Imports:
    - import subprocess  [stdlib]
    - from collections import deque  [stdlib]
    - from typing import List, Optional, Tuple  [stdlib]
  Line count: 36
  __all__: (none)
```

```
FILE: level_1/paths/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from layers.layer_0_core.level_0 import is_kaggle_input  [internal — layer_0_core barrel]
    - from .env_paths import get_run_py_path, get_data_root_path  [internal]
    - from .models import contest_models_dir, contest_model_dir  [internal]
    - from .output_roots import contest_output_root  [internal]
    - from .path_utils import resolve_data_root  [internal]
    - from .runs import contest_runs_root, contest_run_dir  [internal]
    - from .submissions import contest_submission_path  [internal]
  Line count: 27
  __all__: ["get_run_py_path", "get_data_root_path", "contest_models_dir", "contest_model_dir", "contest_output_root", "is_kaggle_input", "resolve_data_root", "contest_runs_root", "contest_run_dir", "contest_submission_path"]
```

```
FILE: level_1/paths/env_paths.py
  Classes: (none)
  Functions:
    - get_run_py_path() -> str
    - get_data_root_path() -> str
  Imports:
    - import os  [stdlib]
    - from pathlib import Path  [stdlib]
    - from layers.layer_1_competition.level_0_infra.level_1.registry import ContestRegistry, get_contest  [internal — level_1.registry]
  Line count: 58
  __all__: (none)
```

```
FILE: level_1/paths/models.py
  Classes: (none)
  Functions:
    - contest_model_dir(paths: ContestPaths, contest_slug: str, model_name: str) -> Path
  Imports:
    - from pathlib import Path  [stdlib]
    - from layers.layer_1_competition.level_0_infra.level_0 import ContestPaths  [internal — level_0_infra.level_0]
    - from layers.layer_1_competition.level_0_infra.level_0 import contest_models_dir  [internal — level_0_infra.level_0 barrel]
  Line count: 15
  __all__: ["contest_model_dir", "contest_models_dir"]
```

```
FILE: level_1/paths/output_roots.py
  Classes: (none)
  Functions:
    - contest_output_root(paths: ContestPaths) -> Path
  Imports:
    - from pathlib import Path  [stdlib]
    - from layers.layer_1_competition.level_0_infra.level_0 import ContestPaths  [internal — level_0_infra.level_0]
  Line count: 14
  __all__: ["contest_output_root"]
```

```
FILE: level_1/paths/path_utils.py
  Classes: (none)
  Functions:
    - resolve_data_root(data_root: Optional[str], paths: ContestPaths) -> str
  Imports:
    - from typing import Optional  [stdlib]
    - from layers.layer_1_competition.level_0_infra.level_0 import ContestPaths  [internal — level_0_infra.level_0]
  Line count: 24
  __all__: ["resolve_data_root"]
```

```
FILE: level_1/paths/runs.py
  Classes: (none)
  Functions:
    - contest_runs_root(paths: ContestPaths, contest_slug: str) -> Path
    - contest_run_dir(paths: ContestPaths, contest_slug: str, run_id: str) -> Path
  Imports:
    - from pathlib import Path  [stdlib]
    - from layers.layer_1_competition.level_0_infra.level_0 import ContestPaths  [internal — level_0_infra.level_0]
  Line count: 23
  __all__: ["contest_run_dir", "contest_runs_root"]
```

```
FILE: level_1/paths/submissions.py
  Classes: (none)
  Functions:
    - contest_submission_path(paths: ContestPaths, filename: str) -> Path
  Imports:
    - from pathlib import Path  [stdlib]
    - from layers.layer_1_competition.level_0_infra.level_0 import ContestPaths  [internal — level_0_infra.level_0]
  Line count: 14
  __all__: ["contest_submission_path"]
```

```
FILE: level_1/pipelines/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .validate_train_submit import ValidateTrainSubmitPipelineResultShell  [internal]
  Line count: 12
  __all__: ["ValidateTrainSubmitPipelineResultShell"]
```

```
FILE: level_1/pipelines/validate_train_submit.py
  Classes:
    - ValidateTrainSubmitPipelineResultShell
        Methods:
                 run(self) -> PipelineResult
  Functions: (none)
  Imports:
    - from dataclasses import dataclass  [stdlib]
    - from typing import Any, Callable, Optional  [stdlib]
    - from layers.layer_1_competition.level_0_infra.level_0 import PipelineResult  [internal — level_0_infra.level_0]
  Line count: 48
  __all__: ["ValidateTrainSubmitPipelineResultShell"]
```

```
FILE: level_1/registry/__init__.py
  Classes: (none)
  Functions: (none)
  Imports:
    - from .contest_registry import ContestRegistry, detect_contest, get_contest, register_contest  [internal]
  Line count: 15
  __all__: ["ContestRegistry", "detect_contest", "get_contest", "register_contest"]
```

```
FILE: level_1/registry/contest_registry.py
  Classes:
    - ContestRegistry
        Methods:
                 register(cls, name: str, config: Type[ContestConfig], data_schema: Type[ContestDataSchema], paths: Type[ContestPaths], post_processor: Type[ContestPostProcessor], training_data_loader: Optional[Callable] = None) -> None
                 get(cls, name: str) -> Optional[Dict[str, Any]]
                 list_contests(cls) -> list
  Functions:
    - register_contest(name: str, config: Type[ContestConfig], data_schema: Type[ContestDataSchema], paths: Type[ContestPaths], post_processor: Type[ContestPostProcessor], training_data_loader: Optional[Callable] = None) -> None
    - get_contest(name: str) -> Dict[str, Type]
    - detect_contest(args: argparse.Namespace) -> str
  Imports:
    - import argparse  [stdlib]
    - import os  [stdlib]
    - from typing import Any, Callable, Dict, Type, Optional  [stdlib]
    - from layers.layer_0_core.level_0 import get_arg  [internal — layer_0_core]
    - from layers.layer_0_core.level_0 import get_logger  [internal — layer_0_core]
    - from layers.layer_1_competition.level_0_infra.level_0 import ContestConfig, ContestDataSchema, ContestPaths, ContestPostProcessor  [internal — level_0_infra.level_0]
  Line count: 150
  __all__: (none)
```

---

## 3. __init__.py Public API Summary

```
INIT: level_1/__init__.py
  Exports (54 strings when submodules load; order = contest __all__ + export + features + grid_search + handlers + notebook + paths + pipelines + registry):
    add_common_contest_args, add_ensemble_weights_arg, add_max_targets_arg, add_models_arg, add_output_csv_arg, add_strategy_arg, add_train_mode_arg, add_validation_stacking_toggle, BasePipeline, build_contest_context, build_grid_search_context, build_run_py_base_command, ContestContext, ContestGridSearchBase, ContestRegistry, contest_model_dir, contest_models_dir, contest_output_root, contest_run_dir, contest_runs_root, contest_submission_path, create_feature_extraction_model, detect_contest, export_model_pipeline, get_command_handlers, get_contest, get_data_root_path, get_notebook_commands_module, get_run_py_path, handle_best_variant_file, handle_just_trained_model, handle_results_file, is_kaggle_input, list_contests_with_notebook_commands, load_best_config_json, load_contest_data, load_contest_training_data, load_training_csv, parse_models_csv, parse_optional_float_list, parse_weights_csv, prepare_regression_model_metadata_dict, register_contest, register_notebook_commands_module, resolve_data_root, resolve_data_root_from_args, resolve_handler_args, run_cli_streaming, set_pretrained_weights_resolver, split_train_val, TwoStageValidateFirstPipelineResultShell, ValidateFirstPipelineResultShell, ValidateFirstRunner, ValidateTrainSubmitPipelineResultShell
  Re-exports from: level_1.contest, level_1.export, level_1.features, level_1.grid_search, level_1.handlers, level_1.notebook, level_1.paths, level_1.pipelines, level_1.registry
```

```
INIT: level_1/contest/__init__.py
  Exports: add_common_contest_args, build_contest_context, ContestContext, load_contest_data, load_contest_training_data, load_training_csv, parse_models_csv, parse_optional_float_list, parse_weights_csv, resolve_data_root_from_args, resolve_handler_args, split_train_val, add_ensemble_weights_arg, add_max_targets_arg, add_models_arg, add_output_csv_arg, add_strategy_arg, add_train_mode_arg, add_validation_stacking_toggle, BasePipeline, ValidateFirstRunner, ValidateFirstPipelineResultShell, TwoStageValidateFirstPipelineResultShell
  Re-exports from: layers.layer_0_core.level_1.pipelines (shells), contest.cli, contest.context, contest.csv_io, contest.splits, contest.data_loading, contest.argparse_builders
```

```
INIT: level_1/export/__init__.py
  Exports: export_model_pipeline, prepare_regression_model_metadata_dict, handle_best_variant_file, handle_just_trained_model, handle_results_file
  Re-exports from: export.metadata_builders, export.source_handlers, export.export_model_pipeline
```

```
INIT: level_1/features/__init__.py
  Exports: create_feature_extraction_model, set_pretrained_weights_resolver
  Re-exports from: features.feature_extractor_factory
```

```
INIT: level_1/grid_search/__init__.py
  Exports: ContestGridSearchBase, load_best_config_json, build_grid_search_context
  Re-exports from: layers.layer_0_core.level_4 (load_best_config_json), grid_search.base, grid_search.context
```

```
INIT: level_1/handlers/__init__.py
  Exports: get_command_handlers
  Re-exports from: handlers.command_handlers
```

```
INIT: level_1/handlers/commands/__init__.py
  Exports: (empty __all__)
  Re-exports from: (none)
```

```
INIT: level_1/notebook/__init__.py
  Exports: build_run_py_base_command, get_notebook_commands_module, list_contests_with_notebook_commands, register_notebook_commands_module, run_cli_streaming
  Re-exports from: notebook.base_commands, notebook.dispatch, notebook.streaming
```

```
INIT: level_1/paths/__init__.py
  Exports: get_run_py_path, get_data_root_path, contest_models_dir, contest_model_dir, contest_output_root, is_kaggle_input, resolve_data_root, contest_runs_root, contest_run_dir, contest_submission_path
  Re-exports from: layer_0_core.level_0 (is_kaggle_input), paths.env_paths, paths.models, paths.output_roots, paths.path_utils, paths.runs, paths.submissions
```

```
INIT: level_1/pipelines/__init__.py
  Exports: ValidateTrainSubmitPipelineResultShell
  Re-exports from: pipelines.validate_train_submit
```

```
INIT: level_1/registry/__init__.py
  Exports: ContestRegistry, detect_contest, get_contest, register_contest
  Re-exports from: registry.contest_registry
```

---

## 4. Import Dependency Map

```
INTERNAL IMPORTS SUMMARY:

From layers.layer_0_core (various numeric levels):
  level_0: get_logger, ensure_dir, get_arg, Command, ConfigValidationError, get_torch, parse_comma_separated
  level_0: is_kaggle_input (via barrel re-export from runtime)
  level_1: create_kfold_splits, get_fold_data, generate_feature_filename, get_model_id
  level_2: simple_average
  level_3: SigLIPExtractor
  level_4: load_csv_raw, load_csv_raw_if_exists, load_json_raw, load_best_config_json, create_vision_model, SigLIPFeatureExtractorAdapter
  level_5: find_trained_model_path, extract_scores_from_json, resolve_best_fold_and_score, ExportPipeline
  level_6: GridSearchBase, PredictPipeline, find_combo_id_from_config
  level_8: TrainPipeline
  level_9: HyperparameterGridSearch, CrossValidateWorkflow, TrainPredictWorkflow

From layers.layer_1_competition.level_0_infra.level_0:
  ContestPaths, ContestConfig, ContestDataSchema, ContestPostProcessor, PipelineResult, create_pipeline_kwargs, get_model_name_from_pretrained, get_pretrained_weights_path, contest_models_dir (via level_0.paths)

From layers.layer_1_competition.level_0_infra.level_1 (same tier, absolute paths in logic files):
  registry: get_contest, ContestRegistry
  paths: get_data_root_path, get_run_py_path
  export.* : feature_filename, metadata_builders, source_handlers
  grid_search.context_types: ContestGridSearchContext
  handlers.handler_context; handlers.commands.* (via command_handlers)
  Package root import in contest/data_loading.py: ContestRegistry, get_contest, load_training_csv, split_train_val

Relative imports in __init__.py / subpackage inits only: .contest, .export, .features, .grid_search, .handlers, .notebook, .paths, .pipelines, .registry, and per-subpackage relative re-exports

From contests packages (level_1_impl / contests_special): none in this tree

Upward / out-of-tier: none detected toward contest implementations from these modules (notebook dispatch registers import paths as strings only)
```

---

## 5. Flags

```
FLAGS:
  (resolved) ~~contest/__init__.py — missing pipeline_shells~~ — shells now imported from `layers.layer_0_core.level_1.pipelines`.
  export/export_model_pipeline.py — comment contains the word "legacy" (Scenario 4 auto-detect).
  paths/path_utils.py — filename uses util-style naming (`path_utils`).
  handlers/commands/*.py — repeated module-level name `make_handler` across seven command modules (intentional factory pattern).
  contest/data_loading.py — imports package root `layers...level_1` for symbols also defined in sibling modules (potential circular import coupling with `level_1/__init__.py`).
  grid_search/base.py — `ContestGridSearchBase.__init__` defines a function-scoped nested class `_SimplePaths` (not visible at module level).
  handlers/commands/__init__.py — 4 lines, `__all__ = []` only (minimal barrel).
  No Python files exceed 300 lines in this package; largest is registry/contest_registry.py (150 lines), export/metadata_builders.py (135 lines), contest/argparse_builders.py (112 lines).
  No third-party imports beyond pandas, numpy, sklearn in scanned modules (plus stdlib).
```

---

## 6. Static scan summary

```
Precheck (precheck_level_1_2026-04-08.md) hints:
  - INFRA_TIER_UPWARD: 0 file(s)
  - INFRA_GENERAL_LEVEL: 0 file(s)
  - DEEP_PATH: 0 file(s)
  - RELATIVE_IN_LOGIC: 0 file(s)
  - PARSE_ERROR: 0 file(s)
  - All listed `.py` files under the scan root were reported as "Clean files" for the above violation kinds.
```
