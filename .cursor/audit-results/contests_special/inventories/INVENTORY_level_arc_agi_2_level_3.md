---
generated: 2026-04-21
audit_scope: contests_special
level_name: level_arc_agi_2_level_3
pass_number: 1
run_id: arc-agi-2-full-recommendations
artifact_kind: inventory
audit_profile: full
---

### INVENTORY: `level_arc_agi_2_level_3`

#### 1. Package & File Tree

```
__init__.py [__init__.py]
  __init__.cpython-311.pyc
  extend_subparsers.cpython-311.pyc
  llm_tta_runner.cpython-311.pyc
  lm_peft_adapter.cpython-311.pyc
  neural_eval_score.cpython-311.pyc
  postprocess_handlers.cpython-311.pyc
  submit_strategy_dispatch.cpython-311.pyc
  trainer_registry.cpython-311.pyc
extend_subparsers.py
lm/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    backend_config.cpython-311.pyc
    backend_inference.cpython-311.pyc
    backend_mock.cpython-311.pyc
    backend_transformers.cpython-311.pyc
    token_helpers.cpython-311.pyc
  backend_inference.py
lm_task_adaptation/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    runner.cpython-311.pyc
    training_rows.cpython-311.pyc
  training_rows.py
neural_eval_score/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    neural.cpython-311.pyc
  neural.py
postprocess_handlers.py
trainer_registry/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    trainer_registry.cpython-311.pyc
  trainer_registry.py
```

#### 2. Per-File Details

```
FILE: __init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - lm
    - lm_task_adaptation
    - neural_eval_score
    - trainer_registry
    - lm.*
    - lm_task_adaptation.*
    - neural_eval_score.*
    - trainer_registry.*
```

```
FILE: extend_subparsers.py
  Classes: (none)
  Functions: extend_subparsers
  Imports (extracted):
    - typing.Any
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.add_validate_data_subparser
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.add_postprocess_subparsers
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.add_submit_subparser
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.add_train_subparser
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.add_train_and_submit_subparser
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.add_tune_subparser
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.add_tune_and_submit_subparser
```

```
FILE: lm/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - backend_inference.Grid
    - backend_inference.SharedTorchLmInference
```

```
FILE: lm/backend_inference.py
  Classes: SharedTorchLmInference
  Functions: (none)
  Imports (extracted):
    - typing.Any
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.arc_grid_to_text_lines
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.eval_teacher_forced_neg_sum_logprob
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.REFERENCE_INNER_LOOP_WALL_SEC
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.inference_turbo_dfs
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.ArcQwenGridChatFormatter
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.resolve_arc_digit_token_ids
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.resolve_newline_token_id
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.resolve_turbo_arc_token_table
```

```
FILE: lm_task_adaptation/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - training_rows.build_task_training_rows
```

```
FILE: lm_task_adaptation/training_rows.py
  Classes: (none)
  Functions: build_task_training_rows
  Imports (extracted):
    - layers.layer_1_competition.level_0_infra.level_0.resolve_collator_token_ids
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.apply_augmentation
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.coerce_arc_grid
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.generate_augmentation_specs
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.train_trim_task_train_pairs_to_token_budget
```

```
FILE: neural_eval_score/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - neural.score_neural_on_evaluation
```

```
FILE: neural_eval_score/neural.py
  Classes: (none)
  Functions: score_neural_on_evaluation
  Imports (extracted):
    - pathlib.Path
    - layers.layer_0_core.level_4.load_json_raw
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.arc_find_first_existing_file
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.eval_solution_grids_for_task
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.score_grid_exact_match
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.predict_grid_from_checkpoint
```

```
FILE: postprocess_handlers.py
  Classes: (none)
  Functions: score_submission_cmd, benchmark_rankers_cmd
  Imports (extracted):
    - argparse
    - layers.layer_0_core.level_0.get_logger
    - layers.layer_1_competition.level_0_infra.level_1.resolve_data_root_from_args
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.pipeline_run_benchmark_rankers_from_artifacts
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.pipeline_run_score_submission
```

```
FILE: trainer_registry/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - trainer_registry.REGISTRY
    - trainer_registry.TrainerFn
    - trainer_registry.get_trainer
    - trainer_registry.list_available_models
    - trainer_registry.logger
```

```
FILE: trainer_registry/trainer_registry.py
  Classes: (none)
  Functions: _train_grid_cnn_v0, get_trainer, list_available_models
  Imports (extracted):
    - typing.Callable
    - typing.Optional
    - layers.layer_0_core.level_0.get_logger
    - layers.layer_0_core.level_0.NamedRegistry
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.run_grid_cnn_training
```

#### 3. Package Role (orchestrator summary)

- Tier **3** under `layers.layer_1_competition.level_1_impl.level_arc_agi_2`.

#### 4. Tests / notebooks

- (Not inventoried in this pass; see repo `tests/` / Kaggle notebooks if present.)

#### 5. Flags / static hints

- Precheck report: `precheck_level_arc_agi_2_level_3_2026-04-21.md` — machine precheck skipped (`torchvision` missing in runner env).

#### 6. Static scan summary

- Same as §5; full `audit_precheck.py` stack did not execute.
