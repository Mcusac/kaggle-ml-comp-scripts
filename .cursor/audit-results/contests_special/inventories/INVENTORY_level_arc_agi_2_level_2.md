---
generated: 2026-04-21
audit_scope: contests_special
level_name: level_arc_agi_2_level_2
pass_number: 1
run_id: arc-agi-2-full-recommendations
artifact_kind: inventory
audit_profile: full
---

### INVENTORY: `level_arc_agi_2_level_2`

#### 1. Package & File Tree

```
__init__.py [__init__.py]
  __init__.cpython-311.pyc
  arc_lm_adaptation.cpython-311.pyc
  arc_lm_backend.cpython-311.pyc
  arc_lm_runtime.cpython-311.pyc
  augmentation_scoring.cpython-311.pyc
  cmd_submit.cpython-311.pyc
  cmd_train_and_submit.cpython-311.pyc
  cmd_tune_and_submit.cpython-311.pyc
  commit_run_artifacts.cpython-311.pyc
  decode_branches.cpython-311.pyc
  decoder.cpython-311.pyc
  ensemble_prediction_bridge.cpython-311.pyc
  eval_ranker_benchmark.cpython-311.pyc
  infer_artifact_store.cpython-311.pyc
  infer_batch_offsets.cpython-311.pyc
  infer_time_deadline.cpython-311.pyc
  inference.cpython-311.pyc
  llm_decoding.cpython-311.pyc
  llm_tta_inference.cpython-311.pyc
  lm_notebook_env_hints.cpython-311.pyc
  lm_task_adaptation.cpython-311.pyc
  pipeline_local_eval.cpython-311.pyc
  ranking.cpython-311.pyc
  reference_ranking.cpython-311.pyc
  stack_policy.cpython-311.pyc
  stack_schema.cpython-311.pyc
  submit_strategy.cpython-311.pyc
  token_helpers.cpython-311.pyc
  train.cpython-311.pyc
  train_completion_mask.cpython-311.pyc
  train_cut_to_token_budget.cpython-311.pyc
  train_grid_text.cpython-311.pyc
  train_pair_shuffle.cpython-311.pyc
  train_task_split.cpython-311.pyc
  train_time_budget.cpython-311.pyc
  trainer_v1_fixed.cpython-311.pyc
  trainer_v2_fixed.cpython-311.pyc
  validate.cpython-311.pyc
cmd_submit.py
cmd_train_and_submit.py
cmd_tune_and_submit.py
decode_branches.py
inference.py
parsers/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    submit.cpython-311.pyc
    train.cpython-311.pyc
    train_submit.cpython-311.pyc
    tune.cpython-311.pyc
    tune_submit.cpython-311.pyc
  submit.py
  train.py
  train_submit.py
  tune.py
  tune_submit.py
pipelines/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    benchmark_rankers.cpython-311.pyc
    score_submission.cpython-311.pyc
  benchmark_rankers.py
  score_submission.py
ranking.py
run/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    finalize.cpython-311.pyc
    run_context.cpython-311.pyc
  run_context.py
scoring/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    augmentation_scoring.cpython-311.pyc
    heuristic_scoring.cpython-311.pyc
    nll_core.cpython-311.pyc
  heuristic_scoring.py
token_helpers.py
train/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    grid_cnn.cpython-311.pyc
    lm_token_budget_trim.cpython-311.pyc
    token_budget.cpython-311.pyc
  grid_cnn.py
  lm_token_budget_trim.py
validate.py
```

#### 2. Per-File Details

```
FILE: __init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - parsers
    - pipelines
    - run
    - scoring
    - train
    - parsers.*
    - pipelines.*
    - run.*
    - scoring.*
    - train.*
```

```
FILE: cmd_submit.py
  Classes: (none)
  Functions: build_submit_command
  Imports (extracted):
    - typing.List
    - typing.Optional
    - layers.layer_1_competition.level_0_infra.level_0.append_run_args
    - layers.layer_1_competition.level_0_infra.level_0.append_strategy
    - layers.layer_1_competition.level_0_infra.level_0.append_tuned_config
    - layers.layer_1_competition.level_0_infra.level_0.resolve_and_append_models
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.append_llm
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.append_submit_args
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.base_cmd
```

```
FILE: cmd_train_and_submit.py
  Classes: (none)
  Functions: build_train_and_submit_command
  Imports (extracted):
    - typing.List
    - typing.Optional
    - layers.layer_1_competition.level_0_infra.level_0.append_run_args
    - layers.layer_1_competition.level_0_infra.level_0.append_strategy
    - layers.layer_1_competition.level_0_infra.level_0.append_train_mode
    - layers.layer_1_competition.level_0_infra.level_0.resolve_and_append_models
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.append_llm
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.append_submit_args
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.base_cmd
```

```
FILE: cmd_tune_and_submit.py
  Classes: (none)
  Functions: build_tune_and_submit_command
  Imports (extracted):
    - typing.List
    - typing.Optional
    - layers.layer_1_competition.level_0_infra.level_0.append_run_args
    - layers.layer_1_competition.level_0_infra.level_0.append_strategy
    - layers.layer_1_competition.level_0_infra.level_0.append_tune_args
    - layers.layer_1_competition.level_0_infra.level_0.resolve_and_append_models
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.append_llm
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.append_submit_args
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.base_cmd
```

```
FILE: decode_branches.py
  Classes: (none)
  Functions: decode_with_cell_probs, decode_with_turbo_lm, decode_with_support_grids
  Imports (extracted):
    - typing.Any
    - typing.Mapping
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.ArcLmBudget
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.LlmTtaDfsConfig
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.apply_augmentation
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.build_cell_probs_from_support_grids
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.collect_llm_tta_support_grids
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.decode_grid_candidates
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.decode_tokens_to_grids
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.ArcQwenGridChatFormatter
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.turbo_wall_end_time
```

```
FILE: inference.py
  Classes: (none)
  Functions: predict_grid_from_checkpoint
  Imports (extracted):
    - pathlib.Path
    - layers.layer_0_core.level_0.get_logger
    - layers.layer_0_core.level_0.get_torch
    - layers.layer_0_core.level_4.load_json_raw
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.CANVAS_SIZE
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.grid_to_one_hot_tensor
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.logits_to_grid
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.TinyGridCNN
```

```
FILE: parsers/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - submit.add_submit_subparser
    - train.add_train_subparser
    - train_submit.add_train_and_submit_subparser
    - tune.add_tune_subparser
    - tune_submit.add_tune_and_submit_subparser
```

```
FILE: parsers/submit.py
  Classes: (none)
  Functions: add_submit_subparser
  Imports (extracted):
    - typing.Any
    - layers.layer_1_competition.level_0_infra.level_0.add_llm_tta_args
    - layers.layer_1_competition.level_0_infra.level_1.add_common_contest_args
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.add_ensemble
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.add_max_targets
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.add_model
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.add_output
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.add_stacking
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.add_strategy
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.add_seed_and_run_context
```

```
FILE: parsers/train.py
  Classes: (none)
  Functions: add_train_subparser
  Imports (extracted):
    - typing.Any
    - layers.layer_1_competition.level_0_infra.level_1.add_common_contest_args
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.add_max_targets
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.add_model
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.add_seed_and_run_context
```

```
FILE: parsers/train_submit.py
  Classes: (none)
  Functions: add_train_and_submit_subparser
  Imports (extracted):
    - typing.Any
    - layers.layer_1_competition.level_0_infra.level_0.add_llm_tta_args
    - layers.layer_1_competition.level_0_infra.level_1.add_common_contest_args
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.add_ensemble
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.add_max_targets
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.add_model
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.add_output
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.add_stacking
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.add_strategy
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.add_seed_and_run_context
```

```
FILE: parsers/tune.py
  Classes: (none)
  Functions: add_tune_subparser
  Imports (extracted):
    - typing.Any
    - layers.layer_1_competition.level_0_infra.level_1.add_common_contest_args
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.add_max_targets
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.add_search_type
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.add_seed_and_run_context
```

```
FILE: parsers/tune_submit.py
  Classes: (none)
  Functions: add_tune_and_submit_subparser
  Imports (extracted):
    - typing.Any
    - layers.layer_1_competition.level_0_infra.level_0.add_llm_tta_args
    - layers.layer_1_competition.level_0_infra.level_1.add_common_contest_args
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.add_ensemble
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.add_max_targets
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.add_model
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.add_output
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.add_search_type
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.add_stacking
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.add_strategy
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.add_seed_and_run_context
```

```
FILE: pipelines/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - benchmark_rankers.pipeline_run_benchmark_rankers_from_artifacts
    - score_submission.log_local_evaluation_score_optional
    - score_submission.logger
    - score_submission.pipeline_run_score_submission
```

```
FILE: pipelines/benchmark_rankers.py
  Classes: (none)
  Functions: pipeline_run_benchmark_rankers_from_artifacts
  Imports (extracted):
    - pathlib.Path
    - typing.Any
    - layers.layer_0_core.level_4.load_json_raw
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.arc_find_first_existing_file
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.eval_build_basekey_truth_map
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.infer_load_decoded_results_from_dir
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.eval_benchmark_rankers
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.eval_safe_mean_max
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.eval_summarize_correct_beam_stats
```

```
FILE: pipelines/score_submission.py
  Classes: (none)
  Functions: pipeline_run_score_submission, log_local_evaluation_score_optional
  Imports (extracted):
    - pathlib.Path
    - typing.Any
    - layers.layer_0_core.level_0.get_logger
    - layers.layer_0_core.level_4.load_json_raw
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.arc_find_first_existing_file
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.eval_parse_task_solution_grids
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.eval_score_submission_two_attempts
```

```
FILE: ranking.py
  Classes: (none)
  Functions: pick_ranked_attempts, build_fallback_attempts
  Imports (extracted):
    - time
    - typing.Any
    - typing.Mapping
    - layers.layer_0_core.level_0.get_logger
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.ArcLmBudget
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.CandidatePrediction
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.LlmTtaDfsConfig
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.coerce_arc_grid
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.empty_arc_grid_like
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.predict_attempts_from_chosen_params
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.rank_candidate_grids
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.ensemble_rank_predictions_reference
```

```
FILE: run/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - run_context.init_run_context
    - run_context.logger
```

```
FILE: run/run_context.py
  Classes: (none)
  Functions: _try_get_gpu_name, init_run_context
  Imports (extracted):
    - os
    - platform
    - sys
    - time
    - pathlib.Path
    - typing.Any
    - typing.Optional
    - layers.layer_0_core.level_0.ensure_dir
    - layers.layer_0_core.level_0.get_logger
    - layers.layer_0_core.level_0.is_kaggle
    - layers.layer_0_core.level_4.save_json
    - layers.layer_1_competition.level_0_infra.level_1.RunContext
    - layers.layer_1_competition.level_0_infra.level_0.generate_run_id
    - layers.layer_1_competition.level_0_infra.level_0.utc_now_iso
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.resolve_run_dir
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.ARC26Paths
    - torch
```

```
FILE: scoring/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - heuristic_scoring.logger
    - heuristic_scoring.score_heuristic_exact_match_on_training
    - heuristic_scoring.score_heuristic_on_evaluation
    - heuristic_scoring.score_heuristic_on_training_challenges
```

```
FILE: scoring/heuristic_scoring.py
  Classes: (none)
  Functions: _first_existing_or_default, score_heuristic_on_training_challenges, score_heuristic_exact_match_on_training, score_heuristic_on_evaluation
  Imports (extracted):
    - pathlib.Path
    - layers.layer_0_core.level_0.get_logger
    - layers.layer_0_core.level_4.load_json_raw
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.arc_find_first_existing_file
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.predict_attempts_for_heuristic
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.cell_match_counts
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.eval_solution_grids_for_task
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.score_grid_exact_match
```

```
FILE: token_helpers.py
  Classes: (none)
  Functions: resolve_arc_digit_token_ids, resolve_turbo_arc_token_table
  Imports (extracted):
    - typing.Any
    - layers.layer_1_competition.level_0_infra.level_0.load_adapter_state_dict
    - layers.layer_1_competition.level_0_infra.level_0.resolve_digit_token_ids
    - layers.layer_1_competition.level_0_infra.level_0.resolve_newline_token_id
    - layers.layer_1_competition.level_0_infra.level_0.resolve_turbo_token_table
    - layers.layer_1_competition.level_0_infra.level_0.torch_dtype_from_config
    - layers.layer_1_competition.level_0_infra.level_0.unsloth_available
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.ArcQwenGridChatFormatter
```

```
FILE: train/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - grid_cnn.DEFAULT_BATCH
    - grid_cnn.DEFAULT_EPOCHS
    - grid_cnn.DEFAULT_LR
    - grid_cnn.logger
    - grid_cnn.run_grid_cnn_training
    - lm_token_budget_trim.Grid
    - lm_token_budget_trim.train_trim_task_train_pairs_to_token_budget
```

```
FILE: train/grid_cnn.py
  Classes: (none)
  Functions: run_grid_cnn_training
  Imports (extracted):
    - pathlib.Path
    - layers.layer_0_core.level_0.ensure_dir
    - layers.layer_0_core.level_0.get_logger
    - layers.layer_0_core.level_0.get_torch
    - layers.layer_0_core.level_1.train_one_epoch
    - layers.layer_0_core.level_4.save_json
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.CANVAS_SIZE
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.NUM_CHANNELS
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.ArcSameShapeGridDataset
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.collect_same_shape_train_pairs
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.TinyGridCNN
```

```
FILE: train/lm_token_budget_trim.py
  Classes: (none)
  Functions: _train_pairs_for_fmt, train_trim_task_train_pairs_to_token_budget
  Imports (extracted):
    - copy
    - typing.Any
    - typing.Mapping
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.ArcQwenGridChatFormatter
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.arc_count_tokens
```

```
FILE: validate.py
  Classes: (none)
  Functions: run_validate_data_pipeline
  Imports (extracted):
    - typing.Optional
    - layers.layer_0_core.level_0.PipelineResult
    - layers.layer_0_core.level_0.get_logger
    - layers.layer_1_competition.level_0_infra.level_0.metadata_merge
    - layers.layer_1_competition.level_0_infra.level_1.RunContext
    - layers.layer_1_competition.level_0_infra.level_1.update_run_metadata
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.validate_arc_inputs
```

#### 3. Package Role (orchestrator summary)

- Tier **2** under `layers.layer_1_competition.level_1_impl.level_arc_agi_2`.

#### 4. Tests / notebooks

- (Not inventoried in this pass; see repo `tests/` / Kaggle notebooks if present.)

#### 5. Flags / static hints

- Precheck report: `precheck_level_arc_agi_2_level_2_2026-04-21.md` — machine precheck skipped (`torchvision` missing in runner env).

#### 6. Static scan summary

- Same as §5; full `audit_precheck.py` stack did not execute.
