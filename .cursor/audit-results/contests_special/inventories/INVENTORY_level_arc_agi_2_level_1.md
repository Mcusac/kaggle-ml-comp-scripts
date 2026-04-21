---
generated: 2026-04-21
audit_scope: contests_special
level_name: level_arc_agi_2_level_1
pass_number: 1
run_id: arc-agi-2-full-recommendations
artifact_kind: inventory
audit_profile: full
---

### INVENTORY: `level_arc_agi_2_level_1`

#### 1. Package & File Tree

```
__init__.py [__init__.py]
  __init__.cpython-311.pyc
  augmentations.cpython-311.pyc
  candidate_scoring.cpython-311.pyc
  dataset_core.cpython-311.pyc
  decoder_dfs.cpython-311.pyc
  ensemble_candidate_bridge.cpython-311.pyc
  ensemble_prediction_bridge.cpython-311.pyc
  ensemble_reference_rankers.cpython-311.pyc
  eval_ranker_benchmark.cpython-311.pyc
  eval_solution_parse.cpython-311.pyc
  eval_submission_scoring.cpython-311.pyc
  eval_teacher_forced_score.cpython-311.pyc
  lm_qwen_chat_format.cpython-311.pyc
  model.cpython-311.pyc
  paths.cpython-311.pyc
  run_tracking.cpython-311.pyc
  scoring.cpython-311.pyc
  submission_two_attempt_build.cpython-311.pyc
  token_decoder.cpython-311.pyc
  tune_llm_weight_presets.cpython-311.pyc
  tune_ranker_comparison.cpython-311.pyc
  tuning_io.cpython-311.pyc
cli/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    append_common_args.cpython-311.pyc
    extend_subparsers.cpython-311.pyc
    registry.cpython-311.pyc
  append_common_args.py
  commands/
    __init__.py [__init__.py]
      __init__.cpython-311.pyc
      build_submit_command.cpython-311.pyc
      build_train_command.cpython-311.pyc
      build_tune_command.cpython-311.pyc
    build_submit_command.py
    build_train_command.py
    build_tune_command.py
  parsers/
    __init__.py [__init__.py]
      __init__.cpython-311.pyc
      common.cpython-311.pyc
      postprocess.cpython-311.pyc
      submit.cpython-311.pyc
      train.cpython-311.pyc
      train_submit.cpython-311.pyc
      tune.cpython-311.pyc
      tune_submit.cpython-311.pyc
      validate_data.cpython-311.pyc
    common.py
    postprocess.py
    validate_data.py
datasets/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    dataset.cpython-311.pyc
    dataset_same_shape.cpython-311.pyc
    dataset_same_shape_pairs.cpython-311.pyc
    loader_utils.cpython-311.pyc
  dataset_same_shape.py
  dataset_same_shape_pairs.py
ensemble_prediction_bridge.py
eval/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    benchmarking_print.cpython-311.pyc
    ranker_benchmark.cpython-311.pyc
    submission_scoring.cpython-311.pyc
  ranker_benchmark.py
  submission_scoring.py
lm/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    chat_format.cpython-311.pyc
    collator.cpython-311.pyc
    formatter_alt.cpython-311.pyc
    lm_attention_patchers.cpython-311.pyc
    trainer.cpython-311.pyc
    trainer_v1_fixed.cpython-311.pyc
    trainer_v2_fixed.cpython-311.pyc
    worker_config.cpython-311.pyc
  chat_format.py
model.py
notebook_commands/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    cmd_train.cpython-311.pyc
    cmd_tune.cpython-311.pyc
    cmd_validate_data.cpython-311.pyc
  cmd_train.py
  cmd_tune.py
  cmd_validate_data.py
paths.py
ranking/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    candidate_scoring.cpython-311.pyc
    ensemble_reference_rankers.cpython-311.pyc
  candidate_scoring.py
  ensemble_reference_rankers.py
run/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    finalize.cpython-311.pyc
    run_context.cpython-311.pyc
    run_dir.cpython-311.pyc
    run_id.cpython-311.pyc
  run_dir.py
runner/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    runner_entry.cpython-311.pyc
  runner_entry.py
stages/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    llm_tta_config.cpython-311.pyc
    metadata_resolvers.cpython-311.pyc
    second_attempt.cpython-311.pyc
    submit.cpython-311.pyc
    train.cpython-311.pyc
    tune.cpython-311.pyc
  llm_tta_config.py
  metadata_resolvers.py
  second_attempt.py
validation/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    validate_challenges.cpython-311.pyc
    validate_data.cpython-311.pyc
    validate_submission_contract.cpython-311.pyc
    validate_task_pair.cpython-311.pyc
  validate_challenges.py
  validate_data.py
  validate_submission_contract.py
  validate_task_pair.py
```

#### 2. Per-File Details

```
FILE: __init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - cli
    - datasets
    - eval
    - lm
    - notebook_commands
    - ranking
    - run
    - runner
    - stages
    - validation
    - cli.*
    - datasets.*
    - eval.*
    - lm.*
    - notebook_commands.*
    - ranking.*
    - run.*
    - runner.*
    - stages.*
    - validation.*
```

```
FILE: cli/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - commands
    - parsers
    - commands.*
    - parsers.*
```

```
FILE: cli/append_common_args.py
  Classes: (none)
  Functions: append_common_args
  Imports (extracted):
    - typing.List
    - typing.Optional
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.append_run_args
```

```
FILE: cli/commands/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - build_submit_command.build_submit_command
    - build_train_command.build_train_command
    - build_tune_command.build_tune_command
```

```
FILE: cli/commands/build_submit_command.py
  Classes: (none)
  Functions: build_submit_command
  Imports (extracted):
    - typing.List
    - typing.Optional
    - layers.layer_1_competition.level_0_infra.level_0.append_ensemble_weights
    - layers.layer_1_competition.level_0_infra.level_0.append_max_targets
    - layers.layer_1_competition.level_0_infra.level_0.append_no_validation_stacking
    - layers.layer_1_competition.level_0_infra.level_0.append_output_csv
    - layers.layer_1_competition.level_0_infra.level_0.append_strategy
    - layers.layer_1_competition.level_0_infra.level_0.append_tuned_config
    - layers.layer_1_competition.level_0_infra.level_0.resolve_and_append_models
    - layers.layer_1_competition.level_0_infra.level_0.append_llm_args
    - layers.layer_1_competition.level_0_infra.level_1.build_run_py_base_command
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.CONTEST
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.append_common_args
```

```
FILE: cli/commands/build_train_command.py
  Classes: (none)
  Functions: build_train_command
  Imports (extracted):
    - typing.List
    - typing.Optional
    - layers.layer_1_competition.level_0_infra.level_0.append_train_mode
    - layers.layer_1_competition.level_0_infra.level_0.resolve_and_append_models
    - layers.layer_1_competition.level_0_infra.level_1.build_run_py_base_command
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.CONTEST
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.append_common_args
```

```
FILE: cli/commands/build_tune_command.py
  Classes: (none)
  Functions: build_tune_command
  Imports (extracted):
    - typing.List
    - typing.Optional
    - layers.layer_1_competition.level_0_infra.level_0.append_max_targets
    - layers.layer_1_competition.level_0_infra.level_0.append_tune_args
    - layers.layer_1_competition.level_0_infra.level_1.build_run_py_base_command
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.CONTEST
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.append_common_args
```

```
FILE: cli/parsers/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - common.add_seed_and_run_context
    - postprocess.add_postprocess_subparsers
    - validate_data.add_validate_data_subparser
```

```
FILE: cli/parsers/common.py
  Classes: (none)
  Functions: add_seed_and_run_context
  Imports (extracted):
    - typing.Any
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.add_run_context
```

```
FILE: cli/parsers/postprocess.py
  Classes: (none)
  Functions: add_postprocess_subparsers
  Imports (extracted):
    - typing.Any
    - layers.layer_1_competition.level_0_infra.level_1.add_common_contest_args
```

```
FILE: cli/parsers/validate_data.py
  Classes: (none)
  Functions: add_validate_data_subparser
  Imports (extracted):
    - typing.Any
    - layers.layer_1_competition.level_0_infra.level_1.add_common_contest_args
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.add_max_targets
```

```
FILE: datasets/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - dataset_same_shape.ArcSameShapeGridDataset
    - dataset_same_shape.torch
    - dataset_same_shape_pairs.collect_same_shape_train_pairs
    - dataset_same_shape_pairs.logger
```

```
FILE: datasets/dataset_same_shape.py
  Classes: ArcSameShapeGridDataset
  Functions: (none)
  Imports (extracted):
    - typing.Any
    - torch.utils.data.Dataset
    - layers.layer_0_core.level_0.get_torch
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.CANVAS_SIZE
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.grid_to_one_hot_tensor
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.pad_grid_to_canvas
```

```
FILE: datasets/dataset_same_shape_pairs.py
  Classes: (none)
  Functions: _find_training_challenges_json, collect_same_shape_train_pairs
  Imports (extracted):
    - pathlib.Path
    - layers.layer_0_core.level_0.get_logger
    - layers.layer_0_core.level_4.load_json_raw
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.TRAINING_CHALLENGE_NAMES
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.arc_find_first_existing_file
```

```
FILE: ensemble_prediction_bridge.py
  Classes: (none)
  Functions: ensemble_candidate_to_guess_dict, ensemble_predictions_to_guess_map, ensemble_rank_predictions_reference
  Imports (extracted):
    - typing.Any
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.CandidatePrediction
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.ENSEMBLE_REFERENCE_RANKERS
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.Grid
```

```
FILE: eval/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - ranker_benchmark.eval_benchmark_rankers
    - ranker_benchmark.eval_run_selection_on_decoded
    - ranker_benchmark.eval_safe_mean_max
    - ranker_benchmark.eval_summarize_correct_beam_stats
    - submission_scoring.eval_count_tasks
    - submission_scoring.eval_score_submission_two_attempts
```

```
FILE: eval/ranker_benchmark.py
  Classes: (none)
  Functions: eval_run_selection_on_decoded, _eval_split_basekey, _eval_num_tasks_per_puzzle, eval_benchmark_rankers, eval_summarize_correct_beam_stats, eval_safe_mean_max
  Imports (extracted):
    - typing.Any
    - typing.Callable
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.arc_grids_equal
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.Grid
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.ensemble_score_full_probmul_3
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.ensemble_score_kgmon
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.DecodedStore
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.GuessDict
```

```
FILE: eval/submission_scoring.py
  Classes: (none)
  Functions: eval_score_submission_two_attempts, eval_count_tasks
  Imports (extracted):
    - typing.Any
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.arc_grids_equal
```

```
FILE: lm/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - chat_format.ArcQwenGridChatFormatter
    - chat_format.Grid
    - chat_format.arc_count_tokens
```

```
FILE: lm/chat_format.py
  Classes: ArcQwenGridChatFormatter
  Functions: arc_count_tokens
  Imports (extracted):
    - dataclasses.dataclass
    - typing.Any
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.MAX_ARC_GRID_DIM
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.arc_grid_to_text_lines
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.arc_text_lines_to_grid
```

```
FILE: model.py
  Classes: TinyGridCNN
  Functions: (none)
  Imports (extracted):
    - torch.nn
    - layers.layer_0_core.level_0.get_torch
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.NUM_CHANNELS
```

```
FILE: notebook_commands/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - cmd_train.build_train_command
    - cmd_tune.build_tune_command
    - cmd_validate_data.build_validate_data_command
```

```
FILE: notebook_commands/cmd_train.py
  Classes: (none)
  Functions: build_train_command
  Imports (extracted):
    - typing.List
    - typing.Optional
    - layers.layer_1_competition.level_0_infra.level_0.append_run_args
    - layers.layer_1_competition.level_0_infra.level_0.resolve_and_append_models
    - layers.layer_1_competition.level_0_infra.level_0.append_train_mode
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.base_cmd
```

```
FILE: notebook_commands/cmd_tune.py
  Classes: (none)
  Functions: build_tune_command
  Imports (extracted):
    - typing.List
    - typing.Optional
    - layers.layer_1_competition.level_0_infra.level_0.append_max_targets
    - layers.layer_1_competition.level_0_infra.level_0.append_run_args
    - layers.layer_1_competition.level_0_infra.level_0.append_tune_args
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.base_cmd
```

```
FILE: notebook_commands/cmd_validate_data.py
  Classes: (none)
  Functions: build_validate_data_command
  Imports (extracted):
    - typing.List
    - typing.Optional
    - layers.layer_1_competition.level_0_infra.level_0.append_max_targets
    - layers.layer_1_competition.level_0_infra.level_0.append_run_args
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.base_cmd
```

```
FILE: paths.py
  Classes: ARC26Paths
  Functions: (none)
  Imports (extracted):
    - pathlib.Path
    - typing.Optional
    - layers.layer_1_competition.level_0_infra.level_0.ContestPaths
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.EVAL_CHALLENGE_NAMES
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.EVAL_SOLUTION_NAMES
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.TEST_CHALLENGE_NAMES
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.TRAINING_CHALLENGE_NAMES
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.TRAINING_SOLUTION_NAMES
```

```
FILE: ranking/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - candidate_scoring.CandidatePrediction
    - candidate_scoring.Grid
    - candidate_scoring.RankedCandidate
    - candidate_scoring.rank_candidate_grids
    - ensemble_reference_rankers.ENSEMBLE_REFERENCE_RANKERS
    - ensemble_reference_rankers.Grid
    - ensemble_reference_rankers.GuessDict
    - ensemble_reference_rankers.ensemble_hashable_grid
    - ensemble_reference_rankers.ensemble_score_full_probmul_3
    - ensemble_reference_rankers.ensemble_score_kgmon
    - ensemble_reference_rankers.ensemble_score_sum
    - ensemble_reference_rankers.reference_hashable_solution
```

```
FILE: ranking/candidate_scoring.py
  Classes: CandidatePrediction, RankedCandidate
  Functions: rank_candidate_grids
  Imports (extracted):
    - collections.defaultdict
    - dataclasses.dataclass
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.grid_int_hash_key
```

```
FILE: ranking/ensemble_reference_rankers.py
  Classes: (none)
  Functions: reference_hashable_solution, ensemble_hashable_grid, _solution_as_grid, _np_mean_empty_nan, ensemble_score_sum, _getter_full_probmul_3, ensemble_score_full_probmul_3, _getter_kgmon, ensemble_score_kgmon
  Imports (extracted):
    - typing.Any
    - typing.Callable
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.grid_int_hash_key
```

```
FILE: run/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - run_dir.default_runs_root
    - run_dir.resolve_run_dir
```

```
FILE: run/run_dir.py
  Classes: (none)
  Functions: default_runs_root, resolve_run_dir
  Imports (extracted):
    - pathlib.Path
    - typing.Optional
    - layers.layer_1_competition.level_0_infra.level_0.ContestRunPathsProtocol
    - layers.layer_1_competition.level_0_infra.level_1.contest_run_dir
    - layers.layer_1_competition.level_0_infra.level_1.contest_runs_root
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.ARC26Paths
```

```
FILE: runner/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - runner_entry.run_entry
```

```
FILE: runner/runner_entry.py
  Classes: (none)
  Functions: run_entry
  Imports (extracted):
    - argparse
    - json
    - os
    - torch.multiprocessing
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.make_local_worker
```

```
FILE: stages/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - llm_tta_config.build_llm_tta_config
    - metadata_resolvers.default_chosen_params
    - metadata_resolvers.get_per_model_entry
    - metadata_resolvers.logger
    - metadata_resolvers.resolve_chosen_params_for_submit
    - metadata_resolvers.resolve_neural_paths_from_entry
    - second_attempt.logger
    - second_attempt.second_attempt_grid
```

```
FILE: stages/llm_tta_config.py
  Classes: (none)
  Functions: build_llm_tta_config
  Imports (extracted):
    - typing.Optional
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.LlmTtaDfsConfig
```

```
FILE: stages/metadata_resolvers.py
  Classes: (none)
  Functions: default_chosen_params, resolve_chosen_params_for_submit, get_per_model_entry, resolve_neural_paths_from_entry
  Imports (extracted):
    - pathlib.Path
    - typing.Any
    - typing.Optional
    - layers.layer_0_core.level_0.get_logger
    - layers.layer_0_core.level_4.load_json_raw
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.DEFAULT_SUBMIT_HEURISTIC
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.load_chosen_params_from_tuned_config
```

```
FILE: stages/second_attempt.py
  Classes: (none)
  Functions: second_attempt_grid
  Imports (extracted):
    - typing.Any
    - layers.layer_0_core.level_0.get_logger
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.predict_attempts_from_chosen_params
```

```
FILE: validation/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - validate_challenges.validate_challenges
    - validate_data.logger
    - validate_data.require_data_root
    - validate_data.validate_arc_inputs
    - validate_submission_contract.validate_submission_contract
    - validate_task_pair.validate_task_pair
```

```
FILE: validation/validate_challenges.py
  Classes: (none)
  Functions: validate_challenges
  Imports (extracted):
    - typing.Any
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.validate_task_pair
```

```
FILE: validation/validate_data.py
  Classes: (none)
  Functions: _read_json_file, _resolve_challenge_path, require_data_root, validate_arc_inputs
  Imports (extracted):
    - json
    - pathlib.Path
    - typing.Any
    - layers.layer_0_core.level_0.get_logger
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.arc_paths.arc_challenge_filenames.EVAL_CHALLENGE_NAMES
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.arc_paths.arc_challenge_filenames.TEST_CHALLENGE_NAMES
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.arc_paths.arc_challenge_filenames.TRAINING_CHALLENGE_NAMES
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.arc_paths.eval_paths.arc_find_first_existing_file
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.validation.validate_challenges.validate_challenges
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.validation.validate_submission_contract.validate_submission_contract
```

```
FILE: validation/validate_submission_contract.py
  Classes: (none)
  Functions: validate_submission_contract
  Imports (extracted):
    - typing.Any
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.validation.validate_grid_shape.is_valid_grid
```

```
FILE: validation/validate_task_pair.py
  Classes: (none)
  Functions: validate_task_pair
  Imports (extracted):
    - typing.Any
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.is_valid_grid
```

#### 3. Package Role (orchestrator summary)

- Tier **1** under `layers.layer_1_competition.level_1_impl.level_arc_agi_2`.

#### 4. Tests / notebooks

- (Not inventoried in this pass; see repo `tests/` / Kaggle notebooks if present.)

#### 5. Flags / static hints

- Precheck report: `precheck_level_arc_agi_2_level_1_2026-04-21.md` — machine precheck skipped (`torchvision` missing in runner env).

#### 6. Static scan summary

- Same as §5; full `audit_precheck.py` stack did not execute.
