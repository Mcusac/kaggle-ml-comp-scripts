---
generated: 2026-04-21
audit_scope: contests_special
level_name: level_arc_agi_2_level_0
pass_number: 1
run_id: arc-agi-2-full-recommendations
artifact_kind: inventory
audit_profile: full
---

### INVENTORY: `level_arc_agi_2_level_0`

#### 1. Package & File Tree

```
__init__.py [__init__.py]
  __init__.cpython-311.pyc
  append_common_args.cpython-311.pyc
  arc_challenge_filenames.cpython-311.pyc
  arc_digit_grid_text.cpython-311.pyc
  arc_eval_paths.cpython-311.pyc
  arc_grids_equal.cpython-311.pyc
  arc_infer_artifact_store.cpython-311.pyc
  arc_lm_adaptation.cpython-311.pyc
  arc_lm_runtime.cpython-311.pyc
  arc_stack_policy.cpython-311.pyc
  args_adapter.cpython-311.pyc
  augmentations.cpython-311.pyc
  candidate_scoring.cpython-311.pyc
  command_llm.cpython-311.pyc
  command_spec1.cpython-311.pyc
  config.cpython-311.pyc
  data_schema.cpython-311.pyc
  dataset.cpython-311.pyc
  dataset_same_shape.cpython-311.pyc
  dataset_same_shape_pairs.cpython-311.pyc
  dataset_utils.cpython-311.pyc
  decoder_dfs.cpython-311.pyc
  digit_grid_text.cpython-311.pyc
  ensemble_reference_rankers.cpython-311.pyc
  eval_paths.cpython-311.pyc
  eval_solution_parse.cpython-311.pyc
  eval_teacher_forced_score.cpython-311.pyc
  grid_hash_key.cpython-311.pyc
  grid_tensor_encoding.cpython-311.pyc
  grids_equal.cpython-311.pyc
  heuristics.cpython-311.pyc
  infer_artifact_store.cpython-311.pyc
  infer_batch_offsets.cpython-311.pyc
  infer_time_deadline.cpython-311.pyc
  kaggle_arc_challenge_paths.cpython-311.pyc
  llm_decoding.cpython-311.pyc
  llm_tta_config.cpython-311.pyc
  llm_tta_grid_utils.cpython-311.pyc
  llm_tta_inference.cpython-311.pyc
  lm_adaptation.cpython-311.pyc
  lm_attention_patcher_repeat_interleave.cpython-311.pyc
  lm_attention_patcher_sdpa.cpython-311.pyc
  lm_attention_patchers.cpython-311.pyc
  lm_notebook_env_hints.cpython-311.pyc
  lm_runtime.cpython-311.pyc
  loader_utils.cpython-311.pyc
  notebook_commands.cpython-311.pyc
  numpy_color_permute.cpython-311.pyc
  numpy_shuffled.cpython-311.pyc
  numpy_solution_validation.cpython-311.pyc
  paths.cpython-311.pyc
  peft.cpython-311.pyc
  post_processor.cpython-311.pyc
  result_logging.cpython-311.pyc
  runner_base.cpython-311.pyc
  runner_entry.cpython-311.pyc
  runner_worker_factory.cpython-311.pyc
  solver_core.cpython-311.pyc
  stack_policy.cpython-311.pyc
  stack_schema.cpython-311.pyc
  stacking_rules.cpython-311.pyc
  submission_two_attempt_build.cpython-311.pyc
  submit_limits.cpython-311.pyc
  submit_rules.cpython-311.pyc
  token_decoder.cpython-311.pyc
  train_completion_mask.cpython-311.pyc
  train_pair_shuffle.cpython-311.pyc
  train_task_split.cpython-311.pyc
  train_time_budget.cpython-311.pyc
  trainer.cpython-311.pyc
  trainer_ddp_loss.cpython-311.pyc
  trainer_v1_fixed.cpython-311.pyc
  trainer_v2_fixed.cpython-311.pyc
  tune_llm_weight_presets.cpython-311.pyc
  tune_ranker_comparison.cpython-311.pyc
  tuning_io.cpython-311.pyc
  validate_challenges.cpython-311.pyc
  validate_data.cpython-311.pyc
  validate_grid_shape.cpython-311.pyc
  validate_submission_contract.cpython-311.pyc
  validate_task_pair.cpython-311.pyc
arc_paths/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    arc_challenge_filenames.cpython-311.pyc
    eval_paths.cpython-311.pyc
    kaggle_arc_challenge_paths.cpython-311.pyc
    paths.cpython-311.pyc
  arc_challenge_filenames.py
  eval_paths.py
  kaggle_arc_challenge_paths.py
config/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    config.cpython-311.pyc
    data_schema.cpython-311.pyc
    post_processor.cpython-311.pyc
  config.py
  data_schema.py
  post_processor.py
decoding/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    decoder_dfs.cpython-311.pyc
    eval_solution_parse.cpython-311.pyc
    eval_teacher_forced_score.cpython-311.pyc
    infer_batch_offsets.cpython-311.pyc
    llm_decoding.cpython-311.pyc
    token_decoder.cpython-311.pyc
  decoder_dfs.py
  eval_solution_parse.py
  eval_teacher_forced_score.py
  infer_batch_offsets.py
  llm_decoding.py
  token_decoder.py
grid/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    digit_grid_text.cpython-311.pyc
    grid_hash_key.cpython-311.pyc
    grid_tensor_encoding.cpython-311.pyc
    grids_equal.cpython-311.pyc
  digit_grid_text.py
  grid_hash_key.py
  grid_tensor_encoding.py
  grids_equal.py
llm_tta/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    llm_tta_config.cpython-311.pyc
    llm_tta_grid_utils.cpython-311.pyc
  llm_tta_grid_utils.py
lm/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    lm_adaptation.cpython-311.pyc
    lm_attention_patcher_repeat_interleave.cpython-311.pyc
    lm_attention_patcher_sdpa.cpython-311.pyc
    lm_attention_patchers.cpython-311.pyc
    lm_runtime.cpython-311.pyc
    solver_core.cpython-311.pyc
    trainer.cpython-311.pyc
    trainer_ddp_loss.cpython-311.pyc
    trainer_v1_fixed.cpython-311.pyc
    trainer_v2_fixed.cpython-311.pyc
  lm_attention_patcher_repeat_interleave.py
  lm_attention_patcher_sdpa.py
ndarray_ops/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    numpy_color_permute.cpython-311.pyc
    numpy_shuffled.cpython-311.pyc
    numpy_solution_validation.cpython-311.pyc
  numpy_color_permute.py
  numpy_shuffled.py
  numpy_solution_validation.py
notebook_commands/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    arg_common.cpython-311.pyc
    base_cmd.cpython-311.pyc
    cmd_submit.cpython-311.pyc
    cmd_train.cpython-311.pyc
    cmd_train_and_submit.cpython-311.pyc
    cmd_tune.cpython-311.pyc
    cmd_tune_and_submit.cpython-311.pyc
    cmd_validate_data.cpython-311.pyc
    llm_args.cpython-311.pyc
    notebook_commands.cpython-311.pyc
    submit_args.cpython-311.pyc
    train_args.cpython-311.pyc
    tune_args.cpython-311.pyc
  base_cmd.py
  llm_args.py
  submit_args.py
peft.py
ranking/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    augmentations.cpython-311.pyc
    candidate_scoring.cpython-311.pyc
    ensemble_reference_rankers.cpython-311.pyc
    heuristics.cpython-311.pyc
    stack_policy.cpython-311.pyc
    submit_limits.cpython-311.pyc
    tuning_io.cpython-311.pyc
  augmentations.py
  heuristics.py
  stack_policy.py
  submit_limits.py
  tuning_io.py
scoring/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    augmentation_scoring.cpython-311.pyc
    fs_helpers.cpython-311.pyc
    grid_metrics.cpython-311.pyc
    heuristic_scoring.cpython-311.pyc
  augmentation_scoring.py
  grid_metrics.py
subparser_blocks/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    common.cpython-311.pyc
    io.cpython-311.pyc
    model.cpython-311.pyc
    run.cpython-311.pyc
    strategy.cpython-311.pyc
    tuning.cpython-311.pyc
  io.py
  model.py
  run.py
  strategy.py
  tuning.py
trainer_v1_fixed.py
trainer_v2_fixed.py
validation/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    validate_challenges.cpython-311.pyc
    validate_data.cpython-311.pyc
    validate_grid_shape.cpython-311.pyc
    validate_submission_contract.cpython-311.pyc
    validate_task_pair.cpython-311.pyc
  validate_grid_shape.py
```

#### 2. Per-File Details

```
FILE: __init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - arc_paths
    - config
    - decoding
    - grid
    - llm_tta
    - lm
    - ndarray_ops
    - notebook_commands
    - ranking
    - scoring
    - subparser_blocks
    - validation
    - arc_paths.*
    - config.*
    - decoding.*
    - grid.*
    - llm_tta.*
    - lm.*
    - ndarray_ops.*
    - notebook_commands.*
    - ranking.*
    - scoring.*
    - subparser_blocks.*
    - validation.*
```

```
FILE: arc_paths/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - arc_challenge_filenames.EVAL_CHALLENGE_NAMES
    - arc_challenge_filenames.EVAL_SOLUTION_NAMES
    - arc_challenge_filenames.TEST_CHALLENGE_NAMES
    - arc_challenge_filenames.TRAINING_CHALLENGE_NAMES
    - arc_challenge_filenames.TRAINING_SOLUTION_NAMES
    - eval_paths.arc_find_first_existing_file
    - kaggle_arc_challenge_paths.arc_kaggle_challenges_json_path
    - kaggle_arc_challenge_paths.arc_kaggle_default_challenge_bundle_root
    - kaggle_arc_challenge_paths.arc_kaggle_evaluation_solutions_json_path
```

```
FILE: arc_paths/arc_challenge_filenames.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
```

```
FILE: arc_paths/eval_paths.py
  Classes: (none)
  Functions: arc_find_first_existing_file
  Imports (extracted):
    - pathlib.Path
```

```
FILE: arc_paths/kaggle_arc_challenge_paths.py
  Classes: (none)
  Functions: _truthy_env, arc_kaggle_default_challenge_bundle_root, arc_kaggle_challenges_json_path, arc_kaggle_evaluation_solutions_json_path
  Imports (extracted):
    - os
```

```
FILE: config/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - config.ARC26Config
    - data_schema.ARC26DataSchema
    - post_processor.ARC26PostProcessor
```

```
FILE: config/config.py
  Classes: ARC26Config
  Functions: (none)
  Imports (extracted):
    - typing.Any
    - layers.layer_1_competition.level_0_infra.level_0.ContestConfig
```

```
FILE: config/data_schema.py
  Classes: ARC26DataSchema
  Functions: (none)
  Imports (extracted):
    - layers.layer_1_competition.level_0_infra.level_0.ContestDataSchema
```

```
FILE: config/post_processor.py
  Classes: ARC26PostProcessor
  Functions: (none)
  Imports (extracted):
    - numpy
    - copy.deepcopy
    - typing.Any
    - layers.layer_1_competition.level_0_infra.level_0.ContestPostProcessor
```

```
FILE: decoding/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - decoder_dfs.GridCandidate
    - decoder_dfs.decode_grid_candidates
    - eval_solution_parse.eval_build_basekey_truth_map
    - eval_solution_parse.eval_parse_task_solution_grids
    - eval_teacher_forced_score.eval_teacher_forced_neg_sum_logprob
    - eval_teacher_forced_score.eval_teacher_forced_neg_sum_logprob_batch
    - eval_teacher_forced_score.torch
    - infer_batch_offsets.infer_group_subkeys_by_test_id
    - infer_batch_offsets.infer_notebook_style_decode_batches
    - llm_decoding.REFERENCE_ARC_TOKENS
    - llm_decoding.REFERENCE_ARC_VOCAB
    - llm_decoding.REFERENCE_ASSISTANT_TOKEN_ID
    - llm_decoding.REFERENCE_EOS_ID
    - llm_decoding.REFERENCE_INNER_LOOP_WALL_SEC
    - llm_decoding.REFERENCE_PAD_ID
    - llm_decoding.REFERENCE_USER_TOKEN_ID
    - llm_decoding.TurboSuffixes
    - llm_decoding.inference_turbo_dfs
    - llm_decoding.torch
    - llm_decoding.turbo_dfs
    - token_decoder.Grid
    - token_decoder.TokenDecodeCandidate
    - token_decoder.decode_tokens_to_grids
```

```
FILE: decoding/decoder_dfs.py
  Classes: GridCandidate
  Functions: _top_k_with_log_probs, decode_grid_candidates
  Imports (extracted):
    - dataclasses.dataclass
    - math.log
```

```
FILE: decoding/eval_solution_parse.py
  Classes: (none)
  Functions: eval_parse_task_solution_grids, eval_build_basekey_truth_map
  Imports (extracted):
    - typing.Any
```

```
FILE: decoding/eval_teacher_forced_score.py
  Classes: (none)
  Functions: eval_teacher_forced_neg_sum_logprob, eval_teacher_forced_neg_sum_logprob_batch
  Imports (extracted):
    - typing.Any
    - layers.layer_0_core.level_0.get_torch
```

```
FILE: decoding/infer_batch_offsets.py
  Classes: (none)
  Functions: infer_group_subkeys_by_test_id, infer_notebook_style_decode_batches
  Imports (extracted):
    - collections.defaultdict
```

```
FILE: decoding/llm_decoding.py
  Classes: (none)
  Functions: turbo_dfs, inference_turbo_dfs
  Imports (extracted):
    - time
    - collections.defaultdict
    - typing.Any
    - typing.Dict
    - typing.List
    - typing.Sequence
    - typing.Tuple
    - layers.layer_0_core.level_0.get_torch
```

```
FILE: decoding/token_decoder.py
  Classes: TokenDecodeCandidate
  Functions: _safe_log_prob, decode_tokens_to_grids
  Imports (extracted):
    - dataclasses.dataclass
    - math.log
    - typing.Callable
```

```
FILE: grid/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - digit_grid_text.Grid
    - digit_grid_text.MAX_ARC_GRID_DIM
    - digit_grid_text.arc_grid_to_text_lines
    - digit_grid_text.arc_is_valid_grid_shape
    - digit_grid_text.arc_text_lines_to_grid
    - grid_hash_key.grid_int_hash_key
    - grid_tensor_encoding.CANVAS_SIZE
    - grid_tensor_encoding.NUM_CHANNELS
    - grid_tensor_encoding.grid_to_one_hot_tensor
    - grid_tensor_encoding.logits_to_grid
    - grid_tensor_encoding.pad_grid_to_canvas
    - grid_tensor_encoding.torch
    - grids_equal.arc_grids_equal
```

```
FILE: grid/digit_grid_text.py
  Classes: (none)
  Functions: arc_grid_to_text_lines, arc_is_valid_grid_shape, arc_text_lines_to_grid
  Imports (extracted):
```

```
FILE: grid/grid_hash_key.py
  Classes: (none)
  Functions: grid_int_hash_key
  Imports (extracted):
    - typing.Any
```

```
FILE: grid/grid_tensor_encoding.py
  Classes: (none)
  Functions: pad_grid_to_canvas, grid_to_one_hot_tensor, logits_to_grid
  Imports (extracted):
    - layers.layer_0_core.level_0.get_torch
```

```
FILE: grid/grids_equal.py
  Classes: (none)
  Functions: arc_grids_equal
  Imports (extracted):
    - typing.Any
```

```
FILE: llm_tta/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - llm_tta_grid_utils.Grid
    - llm_tta_grid_utils.build_cell_probs_from_support_grids
    - llm_tta_grid_utils.coerce_arc_grid
    - llm_tta_grid_utils.collect_llm_tta_support_grids
    - llm_tta_grid_utils.empty_arc_grid_like
```

```
FILE: llm_tta/llm_tta_grid_utils.py
  Classes: (none)
  Functions: coerce_arc_grid, collect_llm_tta_support_grids, build_cell_probs_from_support_grids
  Imports (extracted):
    - typing.Any
    - typing.Mapping
    - layers.layer_1_competition.level_0_infra.level_0.empty_grid_like
    - layers.layer_1_competition.level_0_infra.level_0.llm_tta_augment_seed
    - layers.layer_1_competition.level_0_infra.level_0.llm_tta_grid_hw
```

```
FILE: lm/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - lm_attention_patcher_repeat_interleave.install_repeat_interleave_attention
    - lm_attention_patcher_repeat_interleave.torch
    - lm_attention_patcher_sdpa.install_sdpa_attention
```

```
FILE: lm/lm_attention_patcher_repeat_interleave.py
  Classes: (none)
  Functions: _repeat_interleave_attention, install_repeat_interleave_attention
  Imports (extracted):
    - layers.layer_0_core.level_0.get_torch
    - unsloth.models.qwen3
```

```
FILE: lm/lm_attention_patcher_sdpa.py
  Classes: (none)
  Functions: _sdpa_expand_attention, install_sdpa_attention
  Imports (extracted):
    - torch.nn.functional.scaled_dot_product_attention
    - unsloth.models.qwen3
```

```
FILE: ndarray_ops/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - numpy_color_permute.permute_mod
    - numpy_color_permute.permute_rnd_all_
    - numpy_shuffled.shuffled
    - numpy_solution_validation.is_valid_solution
```

```
FILE: ndarray_ops/numpy_color_permute.py
  Classes: (none)
  Functions: permute_mod, permute_rnd_all_
  Imports (extracted):
    - numpy
```

```
FILE: ndarray_ops/numpy_shuffled.py
  Classes: (none)
  Functions: shuffled
  Imports (extracted):
    - numpy
```

```
FILE: ndarray_ops/numpy_solution_validation.py
  Classes: (none)
  Functions: is_valid_solution
  Imports (extracted):
    - numpy
```

```
FILE: notebook_commands/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - base_cmd.base_cmd
    - llm_args.append_llm
    - submit_args.append_submit_args
```

```
FILE: notebook_commands/base_cmd.py
  Classes: (none)
  Functions: base_cmd
  Imports (extracted):
    - typing.Optional
    - layers.layer_1_competition.level_0_infra.level_1.build_run_py_base_command
```

```
FILE: notebook_commands/llm_args.py
  Classes: (none)
  Functions: append_llm
  Imports (extracted):
    - typing.Any
    - typing.List
    - layers.layer_1_competition.level_0_infra.level_0.argv_command_builders.append_llm_args
```

```
FILE: notebook_commands/submit_args.py
  Classes: (none)
  Functions: append_submit_args
  Imports (extracted):
    - typing.List
    - typing.Optional
    - layers.layer_1_competition.level_0_infra.level_0.append_ensemble_weights
    - layers.layer_1_competition.level_0_infra.level_0.append_max_targets
    - layers.layer_1_competition.level_0_infra.level_0.append_no_validation_stacking
    - layers.layer_1_competition.level_0_infra.level_0.append_output_csv
```

```
FILE: peft.py
  Classes: (none)
  Functions: peft_module, get_peft_model_state_dict, set_peft_model_state_dict
  Imports (extracted):
    - importlib
    - typing.Any
```

```
FILE: ranking/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - augmentations.AugmentationSpec
    - augmentations.Grid
    - augmentations.IDENTITY_AUGMENTATION
    - augmentations.apply_augmentation
    - augmentations.generate_augmentation_specs
    - augmentations.invert_augmentation
    - augmentations.invert_color_permutation
    - heuristics.DEFAULT_SUBMIT_HEURISTIC
    - heuristics.HEURISTIC_QUICK_ORDER
    - heuristics.HEURISTIC_THOROUGH_ORDER
    - heuristics.heuristic_order_for_train_mode
    - heuristics.logger
    - heuristics.predict_attempts_for_heuristic
    - heuristics.predict_attempts_from_chosen_params
    - stack_policy.stack_explain_stacking_requirements
    - stack_policy.stack_raise_if_unsupported_strategy
    - submit_limits.logger
    - submit_limits.read_submit_max_tasks_env
    - tuning_io.load_chosen_params_from_tuned_config
    - tuning_io.logger
```

```
FILE: ranking/augmentations.py
  Classes: AugmentationSpec
  Functions: _copy_grid, _transpose_grid, _rotate90, _apply_color_permutation, invert_color_permutation, apply_augmentation, invert_augmentation, _random_color_permutation, _sample_transform_pairs, generate_augmentation_specs
  Imports (extracted):
    - random
    - dataclasses.dataclass
    - typing.Iterable
```

```
FILE: ranking/heuristics.py
  Classes: (none)
  Functions: _build_blank_grid_like, _most_common_non_zero_color, heuristic_order_for_train_mode, predict_attempts_for_heuristic, predict_attempts_from_chosen_params
  Imports (extracted):
    - copy.deepcopy
    - typing.Any
    - typing.Mapping
    - layers.layer_0_core.level_0.get_logger
```

```
FILE: ranking/stack_policy.py
  Classes: (none)
  Functions: stack_explain_stacking_requirements, stack_raise_if_unsupported_strategy
  Imports (extracted):
```

```
FILE: ranking/submit_limits.py
  Classes: (none)
  Functions: read_submit_max_tasks_env
  Imports (extracted):
    - os
    - layers.layer_0_core.level_0.get_logger
```

```
FILE: ranking/tuning_io.py
  Classes: (none)
  Functions: load_chosen_params_from_tuned_config
  Imports (extracted):
    - pathlib.Path
    - typing.Any
    - layers.layer_0_core.level_0.get_logger
    - layers.layer_0_core.level_4.load_json_raw
```

```
FILE: scoring/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - augmentation_scoring.Grid
    - augmentation_scoring.calc_scores_under_augmentations
    - augmentation_scoring.format_augmented_query_reply_batch
    - augmentation_scoring.format_augmented_query_reply_strings
    - augmentation_scoring.invert_candidate_grid
    - grid_metrics.cell_match_counts
    - grid_metrics.eval_solution_grids_for_task
    - grid_metrics.score_grid_exact_match
```

```
FILE: scoring/augmentation_scoring.py
  Classes: (none)
  Functions: format_augmented_query_reply_strings, format_augmented_query_reply_batch, invert_candidate_grid, calc_scores_under_augmentations
  Imports (extracted):
    - collections.abc.Sequence
    - typing.Any
    - layers.layer_1_competition.level_0_infra.level_0.AggregateMode
    - layers.layer_1_competition.level_0_infra.level_0.aggregate_scores_across_augmentations
    - layers.layer_1_competition.level_0_infra.level_0.calc_scores
    - layers.layer_1_competition.level_0_infra.level_0.calc_scores_chunked
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.AugmentationSpec
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.apply_augmentation
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.invert_augmentation
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.ArcQwenGridChatFormatter
```

```
FILE: scoring/grid_metrics.py
  Classes: (none)
  Functions: eval_solution_grids_for_task, cell_match_counts, score_grid_exact_match
  Imports (extracted):
    - typing.Any
```

```
FILE: subparser_blocks/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - io.add_ensemble
    - io.add_max_targets
    - io.add_output
    - io.add_stacking
    - model.add_model
    - run.add_run_context
    - strategy.STRATEGY_CHOICES
    - strategy.add_strategy
    - tuning.add_search_type
```

```
FILE: subparser_blocks/io.py
  Classes: (none)
  Functions: add_output, add_max_targets, add_ensemble, add_stacking
  Imports (extracted):
    - typing.Any
    - layers.layer_1_competition.level_0_infra.level_1.add_output_csv_arg
    - layers.layer_1_competition.level_0_infra.level_1.add_max_targets_arg
    - layers.layer_1_competition.level_0_infra.level_1.add_ensemble_weights_arg
    - layers.layer_1_competition.level_0_infra.level_1.add_validation_stacking_toggle
```

```
FILE: subparser_blocks/model.py
  Classes: (none)
  Functions: add_model
  Imports (extracted):
    - typing.Any
    - layers.layer_1_competition.level_0_infra.level_1.add_models_arg
```

```
FILE: subparser_blocks/run.py
  Classes: (none)
  Functions: add_run_context
  Imports (extracted):
    - typing.Any
```

```
FILE: subparser_blocks/strategy.py
  Classes: (none)
  Functions: add_strategy
  Imports (extracted):
    - typing.Any
    - layers.layer_1_competition.level_0_infra.level_1.add_strategy_arg
```

```
FILE: subparser_blocks/tuning.py
  Classes: (none)
  Functions: add_search_type
  Imports (extracted):
    - typing.Any
```

```
FILE: trainer_v1_fixed.py
  Classes: UnslothFixedTrainer
  Functions: (none)
  Imports (extracted):
    - unsloth.UnslothTrainer
    - layers.layer_1_competition.level_0_infra.level_0.ddp_safe_loss
```

```
FILE: trainer_v2_fixed.py
  Classes: UnslothV2FixedTrainer
  Functions: (none)
  Imports (extracted):
    - unsloth.UnslothTrainer
    - layers.layer_0_core.level_0.get_torch
    - layers.layer_1_competition.level_0_infra.level_0.ddp_safe_loss
```

```
FILE: validation/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - validate_grid_shape.is_valid_grid
```

```
FILE: validation/validate_grid_shape.py
  Classes: (none)
  Functions: is_valid_grid
  Imports (extracted):
    - typing.Any
```

#### 3. Package Role (orchestrator summary)

- Tier **0** under `layers.layer_1_competition.level_1_impl.level_arc_agi_2`.

#### 4. Tests / notebooks

- (Not inventoried in this pass; see repo `tests/` / Kaggle notebooks if present.)

#### 5. Flags / static hints

- Precheck report: `precheck_level_arc_agi_2_level_0_2026-04-21.md` — machine precheck skipped (`torchvision` missing in runner env).

#### 6. Static scan summary

- Same as §5; full `audit_precheck.py` stack did not execute.
