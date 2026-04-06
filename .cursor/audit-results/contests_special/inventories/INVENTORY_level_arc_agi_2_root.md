---
generated: 2026-04-01
scope: contests_special
level: level_arc_agi_2_root
pass: 1
audit_profile: full
run_id: arc_agi_2_root_missing_audit
---

INVENTORY: level_arc_agi_2_root

Root path:
  C:\Users\mdc0431\OneDrive - UNT System\Documents\Kaggle\code\input\kaggle-ml-comp-scripts\scripts\layers\layer_1_competition\level_1_impl\level_arc_agi_2

Precheck:
  Skipped (environment): scripts/dev/scripts/audit_precheck.py not found

---------------------------------------------------------------------------
1. Package & File Tree
---------------------------------------------------------------------------

level_arc_agi_2/
  __init__.py  (package init)
  registration.py
  RUN_TRACKING.md
  level_0/
    __init__.py  (package init)
    config.py
    data_schema.py
    dataset.py
    heuristics.py
    notebook_commands.py
    paths.py
    post_processor.py
    submit_limits.py
    validate_data.py
  level_1/
    __init__.py  (package init)
    model.py
    run_tracking.py
    scoring.py
    tuning_io.py
  level_2/
    __init__.py  (package init)
    inference.py
    submit_strategy.py
    train.py
  level_3/
    __init__.py  (package init)
    trainer_registry.py
  level_4/
    __init__.py  (package init)
    stages.py
  level_5/
    __init__.py  (package init)
    arc_contest_pipeline.py
    orchestration.py
  level_6/
    __init__.py  (package init)
    handlers.py

---------------------------------------------------------------------------
2. Per-File Details
---------------------------------------------------------------------------

FILE: level_arc_agi_2/__init__.py
  Docstring: ARC-AGI-2 contest implementation package.
  Classes: (none)
  Functions: (none)
  Imports:
    - from . import level_0, level_1, level_2, level_3, level_4
    - from .level_0 import *
    - from .level_1 import *
    - from .level_2 import *
    - from .level_3 import *
    - from .level_4 import *
  Line count: 17
  __all__: ["level_0", "level_1", "level_2", "level_3", "level_4"]

FILE: level_arc_agi_2/registration.py
  Docstring: Register ARC-AGI-2 contest side effects.
  Classes: (none)
  Functions: (none)
  Imports:
    - from layers.layer_1_competition.level_0_infra.level_1 import (register_cli_handlers_module, register_notebook_commands_module, register_contest)
    - from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (ARC26Config, ARC26DataSchema, ARC26Paths, ARC26PostProcessor)
  Line count: 32
  __all__: (none)

FILE: level_arc_agi_2/level_0/__init__.py
  Docstring: ARC-AGI-2 level_0 primitives.
  Classes: (none)
  Functions: (none)
  Imports:
    - from .config import ARC26Config
    - from .data_schema import ARC26DataSchema
    - from .paths import ARC26Paths
    - from .post_processor import ARC26PostProcessor
    - from .pipeline_result import PipelineResult
    - from .dataset import (ArcSameShapeGridDataset, CANVAS_SIZE, NUM_CHANNELS, collect_same_shape_train_pairs, grid_to_one_hot_tensor, logits_to_grid)
    - from .solvers import (DEFAULT_SUBMIT_HEURISTIC, load_chosen_params_from_tuned_config, predict_attempts_for_heuristic, predict_attempts_for_submit_strategy, predict_attempts_from_chosen_params, rank_heuristics_on_training, read_submit_max_tasks_env, score_heuristic_on_evaluation, score_heuristic_on_training_challenges, select_best_heuristic, select_best_heuristic_on_training)
    - from .notebook_commands import (build_submit_command, build_train_and_submit_command, build_train_command, build_tune_and_submit_command, build_tune_command, build_validate_data_command)
    - from .validate_data import validate_arc_inputs
  Line count: 70
  __all__: ["ARC26Config", "ARC26DataSchema", "ARC26Paths", "ARC26PostProcessor", "PipelineResult", "ArcSameShapeGridDataset", "CANVAS_SIZE", "NUM_CHANNELS", "collect_same_shape_train_pairs", "grid_to_one_hot_tensor", "logits_to_grid", "DEFAULT_SUBMIT_HEURISTIC", "load_chosen_params_from_tuned_config", "predict_attempts_for_heuristic", "predict_attempts_for_submit_strategy", "predict_attempts_from_chosen_params", "rank_heuristics_on_training", "read_submit_max_tasks_env", "score_heuristic_on_evaluation", "score_heuristic_on_training_challenges", "select_best_heuristic", "select_best_heuristic_on_training", "build_validate_data_command", "build_train_command", "build_train_and_submit_command", "build_tune_command", "build_tune_and_submit_command", "build_submit_command", "validate_arc_inputs"]

FILE: level_arc_agi_2/level_0/config.py
  Docstring: ARC-AGI-2 contest configuration.
  Classes:
    - ARC26Config(ContestConfig)
        Methods: target_weights(self) -> dict[str, float]
                 target_order(self) -> list[str]
                 primary_targets(self) -> list[str]
                 derived_targets(self) -> list[str]
                 compute_derived_targets(self, predictions: Any) -> Any
  Functions: (none)
  Imports:
    - from typing import Any
    - from layers.layer_1_competition.level_0_infra.level_0 import ContestConfig  [internal]
  Line count: 29
  __all__: (none)

FILE: level_arc_agi_2/level_0/data_schema.py
  Docstring: ARC-AGI-2 schema surface for framework compatibility.
  Classes:
    - ARC26DataSchema(ContestDataSchema)
        Methods: sample_id_column(self) -> str
                 target_columns(self) -> list[str]
                 validate_sample_id(self, sample_id: str) -> bool
  Functions: (none)
  Imports:
    - from layers.layer_1_competition.level_0_infra.level_0 import ContestDataSchema  [internal]
  Line count: 19
  __all__: (none)

FILE: level_arc_agi_2/level_0/paths.py
  Docstring: ARC-AGI-2 path definitions.
  Classes:
    - ARC26Paths(ContestPaths)
        Methods: kaggle_dataset_name(self) -> str
                 kaggle_competition_name(self) -> Optional[str]
                 local_data_path(self) -> str
                 _find_existing(self, candidates: list[str]) -> Path
                 training_challenges_path(self) -> Path
                 training_solutions_path(self) -> Path
                 evaluation_challenges_path(self) -> Path
                 evaluation_solutions_path(self) -> Path
                 test_challenges_path(self) -> Path
                 sample_submission_path(self) -> Path
                 submission_output_path(self) -> Path
  Functions: (none)
  Imports:
    - from pathlib import Path
    - from typing import Optional
    - from layers.layer_1_competition.level_0_infra.level_0 import ContestPaths  [internal]
  Line count: 77
  __all__: (none)

FILE: level_arc_agi_2/level_0/post_processor.py
  Docstring: ARC submission post-processing helpers.
  Classes:
    - ARC26PostProcessor(ContestPostProcessor)
        Methods: apply(self, predictions: np.ndarray) -> np.ndarray
                 normalize_submission(self, submission: dict[str, list[dict[str, Any]]]) -> dict[str, list[dict[str, Any]]]
  Functions: (none)
  Imports:
    - import numpy as np
    - from copy import deepcopy
    - from typing import Any
    - from layers.layer_1_competition.level_0_infra.level_0 import ContestPostProcessor  [internal]
  Line count: 23
  __all__: (none)

FILE: level_arc_agi_2/level_0/dataset.py
  Docstring: Training pairs and tensor encoding for grid CNN (v0: same-shape input/output only).
  Classes:
    - ArcSameShapeGridDataset(Dataset)
        Methods: __init__(self, pairs: list[tuple[list[list[int]], list[list[int]]]], canvas: int = CANVAS_SIZE)
                 __len__(self) -> int
                 __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor, dict[str, Any]]
  Functions:
    - _find_training_json(root: Path) -> Path
    - collect_same_shape_train_pairs(data_root: str) -> list[tuple[list[list[int]], list[list[int]]]]
    - pad_grid_to_canvas(grid: list[list[int]], canvas: int = CANVAS_SIZE, fill: int = 0) -> list[list[int]]
    - grid_to_one_hot_tensor(grid: list[list[int]], canvas: int = CANVAS_SIZE) -> torch.Tensor
    - logits_to_grid(logits: torch.Tensor, orig_h: int, orig_w: int) -> list[list[int]]
  Imports:
    - from pathlib import Path
    - from typing import Any
    - from torch.utils.data import Dataset
    - from layers.layer_0_core.level_0 import get_logger, get_torch  [internal]
    - from layers.layer_1_competition.level_0_infra.level_0 import read_json  [internal]
  Line count: 115
  __all__: (none)

FILE: level_arc_agi_2/level_0/heuristics.py
  Docstring: Baseline heuristics for ARC attempt generation.
  Classes: (none)
  Functions:
    - _build_blank_grid_like(input_grid: list[list[int]]) -> list[list[int]]
    - heuristic_order_for_train_mode(train_mode: str) -> tuple[str, ...]
    - predict_attempts_for_heuristic(input_grid: list[list[int]], heuristic: str) -> tuple[list[list[int]], list[list[int]]]
    - predict_attempts_from_chosen_params(input_grid: list[list[int]], chosen_params: Mapping[str, Any] | None) -> tuple[list[list[int]], list[list[int]]]
  Imports:
    - from copy import deepcopy
    - from typing import Any, Mapping
    - from layers.layer_0_core.level_0 import get_logger  [internal]
  Line count: 54
  __all__: (none)

FILE: level_arc_agi_2/level_0/notebook_commands.py
  Docstring: ARC notebook command builders.
  Classes: (none)
  Functions:
    - build_validate_data_command(data_root: Optional[str] = None, max_targets: int = 0, log_file: Optional[str] = None) -> List[str]
    - build_train_command(data_root: Optional[str] = None, train_mode: str = "end_to_end", models: Optional[List[str]] = None, run_id: Optional[str] = None, run_dir: Optional[str] = None, log_file: Optional[str] = None) -> List[str]
    - build_tune_command(data_root: Optional[str] = None, model: str = "baseline_approx", search_type: str = "quick", max_targets: int = 0, run_id: Optional[str] = None, run_dir: Optional[str] = None, log_file: Optional[str] = None) -> List[str]
    - build_submit_command(data_root: Optional[str] = None, strategy: str = "single", models: Optional[List[str]] = None, output_csv: Optional[str] = None, max_targets: int = 0, ensemble_weights: Optional[List[float]] = None, use_validation_for_stacking: bool = True, run_id: Optional[str] = None, run_dir: Optional[str] = None, log_file: Optional[str] = None, tuned_config_path: Optional[str] = None) -> List[str]
    - build_train_and_submit_command(data_root: Optional[str] = None, train_mode: str = "end_to_end", models: Optional[List[str]] = None, strategy: str = "single", output_csv: Optional[str] = None, max_targets: int = 0, ensemble_weights: Optional[List[float]] = None, use_validation_for_stacking: bool = True, run_id: Optional[str] = None, run_dir: Optional[str] = None, log_file: Optional[str] = None) -> List[str]
    - build_tune_and_submit_command(data_root: Optional[str] = None, model: str = "baseline_approx", search_type: str = "quick", strategy: str = "single", models: Optional[List[str]] = None, output_csv: Optional[str] = None, max_targets: int = 0, ensemble_weights: Optional[List[float]] = None, use_validation_for_stacking: bool = True, run_id: Optional[str] = None, run_dir: Optional[str] = None, log_file: Optional[str] = None) -> List[str]
  Imports:
    - from typing import List, Optional
    - from layers.layer_1_competition.level_0_infra.level_1 import build_run_py_base_command  [internal]
  Line count: 167
  __all__: (none)

FILE: level_arc_agi_2/level_0/submit_limits.py
  Docstring: ARC submission limit: optional environment-variable cap on evaluation tasks.
  Classes: (none)
  Functions:
    - read_submit_max_tasks_env() -> int | None
  Imports:
    - import os
    - from layers.layer_0_core.level_0 import get_logger  [internal]
  Line count: 23
  __all__: (none)

FILE: level_arc_agi_2/level_0/validate_data.py
  Docstring: ARC JSON contract validation.
  Classes: (none)
  Functions:
    - _is_valid_grid(grid: Any) -> bool
    - _validate_task_pair(pair: Any, include_output: bool = True) -> None
    - _validate_challenges(challenges: Any, max_targets: int = 0) -> None
    - _validate_submission_contract(challenges: dict[str, Any], submission: Any) -> None
    - validate_arc_inputs(data_root: str, max_targets: int = 0) -> None
  Imports:
    - from pathlib import Path
    - from typing import Any
    - from layers.layer_0_core.level_0 import get_logger  [internal]
    - from layers.layer_0_core.level_4 import load_json  [internal]
  Line count: 150
  __all__: (none)

FILE: level_arc_agi_2/level_1/__init__.py
  Docstring: ARC level_1: contest-local orchestration support utilities.
  Classes: (none)
  Functions: (none)
  Imports:
    - from layers.layer_1_competition.level_0_infra.level_0 import PipelineResult  [internal]
    - from .model import TinyGridCNN
    - from .run_tracking import (RunContext, copy_artifact_into_run, finalize_run_failure, finalize_run_success, init_run_context, update_run_metadata)
  Line count: 28
  __all__: ["PipelineResult", "RunContext", "TinyGridCNN", "copy_artifact_into_run", "finalize_run_failure", "finalize_run_success", "init_run_context", "update_run_metadata"]

FILE: level_arc_agi_2/level_1/model.py
  Docstring: Small conv model: per-cell class logits on a padded canvas.
  Classes:
    - TinyGridCNN(nn.Module)
        Methods: __init__(self, num_classes: int = NUM_CHANNELS, hidden: int = 64)
                 forward(self, x: torch.Tensor) -> torch.Tensor
  Functions: (none)
  Imports:
    - import torch.nn as nn
    - from layers.layer_0_core.level_0 import get_torch  [internal]
    - from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import NUM_CHANNELS  [internal]
  Line count: 26
  __all__: (none)

FILE: level_arc_agi_2/level_1/run_tracking.py
  Docstring: ARC-AGI-2 run folder + metadata helpers.
  Classes:
    - RunContext
        Methods: artifacts_dir(self) -> Path
                 logs_dir(self) -> Path
                 manifest_path(self) -> Path
                 commands_path(self) -> Path
  Functions:
    - _utc_now_iso() -> str
    - _safe_stage_slug(stage: str) -> str
    - generate_run_id(stage: str, seed: int) -> str
    - default_runs_root(paths: Optional[ContestRunPathsProtocol] = None) -> Path
    - resolve_run_dir(run_id: str, run_dir: Optional[str] = None, paths: Optional[ContestRunPathsProtocol] = None) -> Path
    - _merge_dict(dst: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]
    - _try_get_gpu_name() -> Optional[str]
    - init_run_context(*, stage: str, data_root: str, seed: int, run_id: Optional[str] = None, run_dir: Optional[str] = None, argv: Optional[list[str]] = None, paths: Optional[ContestRunPathsProtocol] = None) -> RunContext
    - update_run_metadata(run: RunContext, patch: dict[str, Any]) -> None
    - finalize_run_success(run: RunContext) -> None
    - finalize_run_failure(run: RunContext, error: Exception) -> None
    - copy_artifact_into_run(run: RunContext, *, src: Path, dest_name: str) -> Path
  Imports:
    - import os
    - import platform
    - import shutil
    - import sys
    - import time
    - from dataclasses import dataclass
    - from datetime import datetime, timezone
    - from pathlib import Path
    - from typing import Any, Optional
    - from layers.layer_0_core.level_0 import ensure_dir, get_logger, is_kaggle  [internal]
    - from layers.layer_1_competition.level_0_infra.level_0 import (ensure_run_dir, read_json, write_json, ContestRunPathsProtocol, contest_run_dir, contest_runs_root)  [internal]
  Line count: 243
  __all__: (none)

FILE: level_arc_agi_2/level_1/scoring.py
  Docstring: ARC heuristic scoring: per-cell accuracy on training and evaluation corpora.
  Classes: (none)
  Functions:
    - _find_existing(root: Path, names: list[str]) -> Path
    - _load_json_path(path: Path) -> Any
    - _eval_solution_grids_for_task(solutions_obj: Any, task_id: str, n_tests: int) -> list[list[list[int]] | None]
    - _cell_match_counts(pred: list[list[int]], truth: list[list[int]]) -> tuple[int, int]
    - score_heuristic_on_training_challenges(data_root: str, heuristic: str, *, max_tasks: int = 0, max_pairs_per_task: int = 0) -> float
    - score_heuristic_on_evaluation(data_root: str, heuristic: str, *, max_tasks: int = 0, max_targets: int = 0) -> float
    - rank_heuristics_on_training(data_root: str, heuristic_order: tuple[str, ...], *, max_tasks: int = 0, max_pairs_per_task: int = 0) -> list[tuple[str, float]]
    - select_best_heuristic_on_training(data_root: str, train_mode: str, *, max_targets: int = 0) -> tuple[dict[str, Any], dict[str, float]]
    - select_best_heuristic(data_root: str, search_type: str, *, max_targets: int = 0) -> tuple[dict[str, Any], dict[str, float]]
  Imports:
    - from pathlib import Path
    - from typing import Any
    - from layers.layer_0_core.level_0 import get_logger  [internal]
    - from layers.layer_1_competition.level_0_infra.level_0 import read_json  [internal]
    - from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (DEFAULT_SUBMIT_HEURISTIC, HEURISTIC_QUICK_ORDER, HEURISTIC_THOROUGH_ORDER, predict_attempts_for_heuristic, read_submit_max_tasks_env)  [internal]
  Line count: 289
  __all__: (none)

FILE: level_arc_agi_2/level_1/tuning_io.py
  Docstring: Tuned-config IO: load chosen_params from a best_config.json produced by the tuning phase.
  Classes: (none)
  Functions:
    - load_chosen_params_from_tuned_config(path: str | None) -> dict[str, Any] | None
  Imports:
    - from pathlib import Path
    - from typing import Any
    - from layers.layer_0_core.level_0 import get_logger  [internal]
    - from layers.layer_1_competition.level_0_infra.level_0 import read_json  [internal]
  Line count: 33
  __all__: (none)

FILE: level_arc_agi_2/level_2/__init__.py
  Docstring: ARC level_2: training + inference utilities (no orchestration).
  Classes: (none)
  Functions: (none)
  Imports:
    - from .inference import predict_grid_from_checkpoint
    - from .train import run_grid_cnn_training
  Line count: 9
  __all__: ["predict_grid_from_checkpoint", "run_grid_cnn_training"]

FILE: level_arc_agi_2/level_2/inference.py
  Docstring: Load checkpoint and predict output grid for a test input (v0 trim-to-input-size).
  Classes: (none)
  Functions:
    - predict_grid_from_checkpoint(input_grid: list[list[int]], checkpoint_path: str | Path, train_config_path: str | Path) -> list[list[int]]
  Imports:
    - from pathlib import Path
    - from layers.layer_0_core.level_0 import get_logger, get_torch  [internal]
    - from layers.layer_1_competition.level_0_infra.level_0 import read_json  [internal]
    - from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import CANVAS_SIZE, grid_to_one_hot_tensor  [internal]
    - from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import TinyGridCNN  [internal]
  Line count: 45
  __all__: (none)

FILE: level_arc_agi_2/level_2/submit_strategy.py
  Docstring: Submit-strategy dispatch: produces two attempt grids for a given strategy.
  Classes: (none)
  Functions:
    - predict_attempts_for_submit_strategy(input_grid: list[list[int]], *, strategy: str, chosen_params: Mapping[str, Any] | None, data_root: str | None, train_mode: str = "end_to_end", max_pairs_per_task: int = 0) -> tuple[list[list[int]], list[list[int]]]
  Imports:
    - from typing import Any, Mapping
    - from layers.layer_0_core.level_0 import get_logger  [internal]
    - from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (heuristic_order_for_train_mode, predict_attempts_for_heuristic, predict_attempts_from_chosen_params, read_submit_max_tasks_env)  [internal]
    - from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (rank_heuristics_on_training)  [internal]
  Line count: 77
  __all__: (none)

FILE: level_arc_agi_2/level_2/train.py
  Docstring: Train TinyGridCNN and persist checkpoint + train_config.json.
  Classes: (none)
  Functions:
    - run_grid_cnn_training(data_root: str, output_dir: str, *, epochs: int | None = None) -> None
  Imports:
    - from pathlib import Path
    - from layers.layer_0_core.level_0 import ensure_dir, get_logger, get_torch  [internal]
    - from layers.layer_0_core.level_1 import train_one_epoch  [internal]
    - from layers.layer_1_competition.level_0_infra.level_0 import write_json  [internal]
    - from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (CANVAS_SIZE, NUM_CHANNELS, ArcSameShapeGridDataset, collect_same_shape_train_pairs)  [internal]
    - from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import TinyGridCNN  [internal]
  Line count: 80
  __all__: (none)

FILE: level_arc_agi_2/level_3/__init__.py
  Docstring: ARC level_3: model trainer registry.
  Classes: (none)
  Functions: (none)
  Imports:
    - from .trainer_registry import get_trainer, list_available_models
  Line count: 8
  __all__: ["get_trainer", "list_available_models"]

FILE: level_arc_agi_2/level_3/trainer_registry.py
  Docstring: Register ARC trainable models (neural + future): RNA3D-style ``(data_root, output_dir)`` trainers.
  Classes: (none)
  Functions:
    - _train_grid_cnn_v0(data_root: str, output_dir: str) -> None
    - get_trainer(model_name: str) -> Optional[TrainerFn]
    - list_available_models() -> list[str]
  Imports:
    - from typing import Callable, Optional
    - from layers.layer_0_core.level_0 import get_logger  [internal]
    - from layers.layer_1_competition.level_0_infra.level_0 import NamedRegistry  [internal]
    - from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2 import run_grid_cnn_training  [internal]
  Line count: 28
  __all__: (none)

FILE: level_arc_agi_2/level_4/__init__.py
  Docstring: ARC level_4: path-returning pipeline stages (train/tune/submit).
  Classes: (none)
  Functions: (none)
  Imports:
    - from .stages import (run_submission_pipeline, run_train_pipeline, run_tune_pipeline)
  Line count: 13
  __all__: ["run_submission_pipeline", "run_train_pipeline", "run_tune_pipeline"]

FILE: level_arc_agi_2/level_4/stages.py
  Docstring: Path-returning ARC pipeline stages (train / tune / submit).
  Classes: (none)
  Functions:
    - _default_chosen_params() -> dict[str, Any]
    - _resolve_chosen_params_for_submit(tuned_config_path: Optional[str], train_metadata_json: Optional[str], primary_model: str) -> dict[str, Any] | None
    - _get_per_model_entry(train_metadata_json: Optional[str], model_name: str) -> dict[str, Any] | None
    - _resolve_neural_paths_from_entry(entry: dict[str, Any] | None) -> tuple[Path | None, Path | None]
    - _second_attempt_grid(input_grid: list[list[int]], *, strategy: str, chosen_params: dict[str, Any] | None, data_root: str, train_mode: str, max_pairs_per_task: int) -> list[list[int]]
    - run_train_pipeline(data_root: str, train_mode: str, models: list[str], run_ctx: Optional[RunContext] = None, max_targets: int = 0) -> Path
    - run_tune_pipeline(data_root: str, model_name: str, search_type: str = "quick", max_targets: int = 0, run_ctx: Optional[RunContext] = None) -> Path
    - run_submission_pipeline(data_root: str, strategy: str, output_json: Optional[str] = None, max_targets: int = 0, run_ctx: Optional[RunContext] = None, tuned_config_path: Optional[str] = None, train_metadata_json: Optional[str] = None, models: Optional[list[str]] = None, neural_checkpoint_path: Optional[str] = None, neural_train_config_path: Optional[str] = None, train_mode: str = "end_to_end") -> Path
  Imports:
    - from pathlib import Path
    - from typing import Any, Optional
    - from layers.layer_0_core.level_0 import ensure_dir, get_logger  [internal]
    - from layers.layer_1_competition.level_0_infra.level_0 import contest_models_dir, read_json, write_json  [internal]
    - from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (ARC26Paths, ARC26PostProcessor, DEFAULT_SUBMIT_HEURISTIC, load_chosen_params_from_tuned_config, predict_attempts_for_heuristic, predict_attempts_from_chosen_params, rank_heuristics_on_training, read_submit_max_tasks_env, select_best_heuristic, select_best_heuristic_on_training, _heuristic_order_for_train_mode, RunContext, copy_artifact_into_run, finalize_run_failure, finalize_run_success, update_run_metadata)  [internal]
    - from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2 import (predict_grid_from_checkpoint, predict_attempts_for_submit_strategy)  [internal]
    - from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3 import get_trainer, list_available_models  [internal]
  Line count: 390
  __all__: (none)

FILE: level_arc_agi_2/level_5/__init__.py
  Docstring: Orchestration for ARC AGI 2 competition.
  Classes: (none)
  Functions: (none)
  Imports:
    - from .orchestration import (run_validate_data_pipeline, run_train_pipeline_result, run_tune_pipeline_result, run_submission_pipeline_result, run_train_and_submit_pipeline_result, run_tune_and_submit_pipeline_result)
  Line count: 19
  __all__: ["run_validate_data_pipeline", "run_train_pipeline_result", "run_tune_pipeline_result", "run_submission_pipeline_result", "run_train_and_submit_pipeline_result", "run_tune_and_submit_pipeline_result"]

FILE: level_arc_agi_2/level_5/arc_contest_pipeline.py
  Docstring: Adapter implementing ``ContestPipelineProtocol`` for ARC path-based stages.
  Classes:
    - ArcContestPipeline
        Methods: train_pipeline(self, data_root: str, **kwargs: Any) -> Optional[Path]
                 submit_pipeline(self, data_root: str, strategy: str, **kwargs: Any) -> Path
                 tune_pipeline(self, data_root: str, **kwargs: Any) -> Optional[Path]
  Functions: (none)
  Imports:
    - from pathlib import Path
    - from typing import Any, Optional
    - from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_4 import (run_submission_pipeline, run_train_pipeline, run_tune_pipeline)  [internal]
  Line count: 61
  __all__: (none)

FILE: level_arc_agi_2/level_5/orchestration.py
  Docstring: Validation and PipelineResult-oriented orchestration (including composites).
  Classes: (none)
  Functions:
    - run_validate_data_pipeline(*, data_root: str, max_targets: int = 0, run_ctx: Optional[RunContext] = None) -> PipelineResult
    - run_train_pipeline_result(*, data_root: str, train_mode: str, models: list[str], max_targets: int = 0, run_ctx: Optional[RunContext] = None, validate_first: bool = True) -> PipelineResult
    - run_tune_pipeline_result(*, data_root: str, model_name: str, search_type: str = "quick", max_targets: int = 0, run_ctx: Optional[RunContext] = None, validate_first: bool = True) -> PipelineResult
    - run_submission_pipeline_result(*, data_root: str, strategy: str, output_json: Optional[str] = None, max_targets: int = 0, run_ctx: Optional[RunContext] = None, validate_first: bool = True, tuned_config_path: Optional[str] = None, train_metadata_json: Optional[str] = None, models: Optional[list[str]] = None, neural_checkpoint_path: Optional[str] = None, neural_train_config_path: Optional[str] = None, train_mode: str = "end_to_end") -> PipelineResult
    - run_train_and_submit_pipeline_result(*, data_root: str, train_mode: str, models: list[str], strategy: str, output_json: Optional[str] = None, max_targets: int = 0, run_ctx: Optional[RunContext] = None, validate_first: bool = True) -> PipelineResult
    - run_tune_and_submit_pipeline_result(*, data_root: str, model_name: str, search_type: str = "quick", strategy: str, output_json: Optional[str] = None, max_targets: int = 0, run_ctx: Optional[RunContext] = None, validate_first: bool = True) -> PipelineResult
  Imports:
    - from typing import Optional
    - from layers.layer_1_competition.level_0_infra.level_0 import (run_pipeline_result_with_validation_first, ValidateTrainSubmitPipelineResultShell, ArtifactKeys, capture_config_paths, capture_submission_paths, metadata_merge, validate_arc_inputs)  [internal]
    - from layers.layer_1_competition.level_0_infra.level_1 import (TwoStageValidateFirstPipelineResultShell, run_two_stage_pipeline_result_with_validation_first, PipelineResult, RunContext, update_run_metadata)  [internal]
    - from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_4 import (run_submission_pipeline, run_train_pipeline, run_tune_pipeline)  [internal]
  Line count: 270
  __all__: (none)

FILE: level_arc_agi_2/level_6/__init__.py
  Docstring: Orchestration for ARC AGI 2 competition.
  Classes: (none)
  Functions: (none)
  Imports:
    - from .handlers import (extend_subparsers, validate_data, train, tune, submit, train_and_submit, tune_and_submit, get_handlers)
  Line count: 23
  __all__: ["extend_subparsers", "validate_data", "train", "tune", "submit", "train_and_submit", "tune_and_submit", "get_handlers"]

FILE: level_arc_agi_2/level_6/handlers.py
  Docstring: ARC contest handlers.
  Classes: (none)
  Functions:
    - _build_run_ctx(args: argparse.Namespace, stage: str) -> Any
    - _log_result(result: PipelineResult) -> None
    - extend_subparsers(subparsers: Any) -> None
    - validate_data(args: argparse.Namespace) -> None
    - train(args: argparse.Namespace) -> None
    - tune(args: argparse.Namespace) -> None
    - submit(args: argparse.Namespace) -> None
    - train_and_submit(args: argparse.Namespace) -> None
    - tune_and_submit(args: argparse.Namespace) -> None
    - get_handlers() -> dict[str, Callable[[argparse.Namespace], None]]
  Imports:
    - import argparse
    - from typing import Any, Callable
    - from layers.layer_0_core.level_0 import get_logger  [internal]
    - from layers.layer_1_competition.level_0_infra.level_1 import (add_common_contest_args, add_ensemble_weights_arg, add_max_targets_arg, add_models_arg, add_output_csv_arg, add_strategy_arg, add_train_mode_arg, add_validation_stacking_toggle, parse_models_csv, parse_optional_float_list, resolve_data_root_from_args, PipelineResult, init_run_context)  [internal]
    - from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_5 import (run_submission_pipeline_result, run_train_and_submit_pipeline_result, run_train_pipeline_result, run_tune_and_submit_pipeline_result, run_tune_pipeline_result, run_validate_data_pipeline)  [internal]
  Line count: 263
  __all__: (none)

---------------------------------------------------------------------------
3. __init__.py Public API Summary
---------------------------------------------------------------------------

INIT: level_arc_agi_2/__init__.py
  Exports: (via star imports) everything exported by level_0..level_4 plus module attributes
  Explicit __all__: level_0, level_1, level_2, level_3, level_4
  Re-exports from: level_arc_agi_2.level_0, level_arc_agi_2.level_1, level_arc_agi_2.level_2, level_arc_agi_2.level_3, level_arc_agi_2.level_4

INIT: level_arc_agi_2/level_0/__init__.py
  Exports (explicit __all__): ARC26Config, ARC26DataSchema, ARC26Paths, ARC26PostProcessor, PipelineResult, ArcSameShapeGridDataset, CANVAS_SIZE, NUM_CHANNELS, collect_same_shape_train_pairs, grid_to_one_hot_tensor, logits_to_grid, DEFAULT_SUBMIT_HEURISTIC, load_chosen_params_from_tuned_config, predict_attempts_for_heuristic, predict_attempts_for_submit_strategy, predict_attempts_from_chosen_params, rank_heuristics_on_training, read_submit_max_tasks_env, score_heuristic_on_evaluation, score_heuristic_on_training_challenges, select_best_heuristic, select_best_heuristic_on_training, build_validate_data_command, build_train_command, build_train_and_submit_command, build_tune_command, build_tune_and_submit_command, build_submit_command, validate_arc_inputs
  Re-exports from: level_0.config, level_0.data_schema, level_0.paths, level_0.post_processor, level_0.pipeline_result, level_0.dataset, level_0.solvers, level_0.notebook_commands, level_0.validate_data

INIT: level_arc_agi_2/level_1/__init__.py
  Exports (explicit __all__): PipelineResult, RunContext, TinyGridCNN, copy_artifact_into_run, finalize_run_failure, finalize_run_success, init_run_context, update_run_metadata
  Re-exports from: level_1.model, level_1.run_tracking, layers.layer_1_competition.level_0_infra.level_0

INIT: level_arc_agi_2/level_2/__init__.py
  Exports (explicit __all__): predict_grid_from_checkpoint, run_grid_cnn_training
  Re-exports from: level_2.inference, level_2.train

INIT: level_arc_agi_2/level_3/__init__.py
  Exports (explicit __all__): get_trainer, list_available_models
  Re-exports from: level_3.trainer_registry

INIT: level_arc_agi_2/level_4/__init__.py
  Exports (explicit __all__): run_submission_pipeline, run_train_pipeline, run_tune_pipeline
  Re-exports from: level_4.stages

INIT: level_arc_agi_2/level_5/__init__.py
  Exports (explicit __all__): run_validate_data_pipeline, run_train_pipeline_result, run_tune_pipeline_result, run_submission_pipeline_result, run_train_and_submit_pipeline_result, run_tune_and_submit_pipeline_result
  Re-exports from: level_5.orchestration

INIT: level_arc_agi_2/level_6/__init__.py
  Exports (explicit __all__): extend_subparsers, validate_data, train, tune, submit, train_and_submit, tune_and_submit, get_handlers
  Re-exports from: level_6.handlers

---------------------------------------------------------------------------
4. Import Dependency Map
---------------------------------------------------------------------------

INTERNAL IMPORTS SUMMARY (by imported-from module):

  From layers.layer_0_core.level_0  [internal]
    - get_logger: level_0/dataset.py, level_0/heuristics.py, level_0/submit_limits.py, level_0/validate_data.py, level_1/scoring.py, level_2/inference.py, level_2/train.py, level_3/trainer_registry.py, level_4/stages.py, level_6/handlers.py
    - get_torch: level_0/dataset.py, level_1/model.py, level_2/inference.py, level_2/train.py
    - ensure_dir: level_1/run_tracking.py, level_2/train.py, level_4/stages.py
    - is_kaggle: level_1/run_tracking.py

  From layers.layer_0_core.level_1  [internal]
    - train_one_epoch: level_2/train.py

  From layers.layer_0_core.level_4  [internal]
    - load_json: level_0/validate_data.py

  From layers.layer_1_competition.level_0_infra.level_0  [internal]
    - ContestConfig: level_0/config.py
    - ContestDataSchema: level_0/data_schema.py
    - ContestPaths: level_0/paths.py
    - ContestPostProcessor: level_0/post_processor.py
    - read_json: level_0/dataset.py, level_1/scoring.py, level_1/tuning_io.py, level_2/inference.py, level_4/stages.py
    - write_json: level_1/run_tracking.py, level_2/train.py, level_4/stages.py
    - ensure_run_dir / ContestRunPathsProtocol / contest_run_dir / contest_runs_root: level_1/run_tracking.py
    - contest_models_dir: level_4/stages.py
    - NamedRegistry: level_3/trainer_registry.py
    - run_pipeline_result_with_validation_first / ValidateTrainSubmitPipelineResultShell / ArtifactKeys / capture_config_paths / capture_submission_paths / metadata_merge / validate_arc_inputs: level_5/orchestration.py
    - PipelineResult (type): level_1/__init__.py (re-export)

  From layers.layer_1_competition.level_0_infra.level_1  [internal]
    - build_run_py_base_command: level_0/notebook_commands.py
    - register_contest / register_notebook_commands_module / register_cli_handlers_module: registration.py
    - CLI arg helpers + parsers + resolve_data_root_from_args: level_6/handlers.py
    - PipelineResult / init_run_context: level_6/handlers.py
    - TwoStageValidateFirstPipelineResultShell / run_two_stage_pipeline_result_with_validation_first / PipelineResult / RunContext / update_run_metadata: level_5/orchestration.py

  From layers.layer_1_competition.level_1_impl.level_arc_agi_2 (same package)  [internal]
    - Fully-qualified imports used throughout:
        - ...level_0: NUM_CHANNELS, CANVAS_SIZE, grid_to_one_hot_tensor, ArcSameShapeGridDataset, collect_same_shape_train_pairs, read_submit_max_tasks_env, heuristic helpers (various)
        - ...level_1: TinyGridCNN, run tracking helpers, scoring helpers
        - ...level_2: training/inference helpers
        - ...level_3: model trainer registry
        - ...level_4: stages
        - ...level_5: orchestration pipelines

  Relative imports (in-package)
    - Used in __init__.py modules for aggregation and re-export (level_arc_agi_2/__init__.py; level_*/*/__init__.py).

---------------------------------------------------------------------------
5. Flags
---------------------------------------------------------------------------

FLAGS:
  - level_4/stages.py — 390 lines (>300)
  - level_2/__init__.py — 9 lines (<10)
  - level_3/__init__.py — 8 lines (<10)
  - level_0/__init__.py — imports `.pipeline_result` and `.solvers`, but no corresponding `pipeline_result.py` or `solvers.py` exists in this package tree
