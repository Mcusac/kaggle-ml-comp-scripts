---
generated: 2026-04-21
audit_scope: contests_special
level_name: level_arc_agi_2_level_4
pass_number: 1
run_id: arc-agi-2-full-recommendations
artifact_kind: inventory
audit_profile: full
---

### INVENTORY: `level_arc_agi_2_level_4`

#### 1. Package & File Tree

```
__init__.py [__init__.py]
  __init__.cpython-311.pyc
  pipeline_local_eval.cpython-311.pyc
  stages.cpython-311.pyc
  submit_strategy_dispatch.cpython-311.pyc
llm_tta_runner/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    backend_session.cpython-311.pyc
    decode_branches.cpython-311.pyc
    runner.cpython-311.pyc
  backend_session.py
lm/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    backend_config.cpython-311.pyc
    backend_transformers.cpython-311.pyc
    backend_unsloth.cpython-311.pyc
  backend_config.py
  backend_transformers.py
  backend_unsloth.py
lm_task_adaptation/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    runner.cpython-311.pyc
  runner.py
stages/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    submit.cpython-311.pyc
    train.cpython-311.pyc
    tune.cpython-311.pyc
  train.py
  tune.py
```

#### 2. Per-File Details

```
FILE: __init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - llm_tta_runner
    - lm
    - lm_task_adaptation
    - stages
    - llm_tta_runner.*
    - lm.*
    - lm_task_adaptation.*
    - stages.*
```

```
FILE: llm_tta_runner/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - backend_session.logger
    - backend_session.prepare_llm_tta_backend
    - backend_session.restore_adapter_safely
```

```
FILE: llm_tta_runner/backend_session.py
  Classes: (none)
  Functions: prepare_llm_tta_backend, restore_adapter_safely
  Imports (extracted):
    - typing.Any
    - typing.Callable
    - typing.Mapping
    - layers.layer_0_core.level_0.get_logger
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.ArcLmAdaptationConfig
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.LlmTtaDfsConfig
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.run_task_adaptation
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.per_task_adaptation_should_run
    - lm.backend_config.ArcLmBackendConfig
    - lm.backend_config.build_arc_lm_backend
```

```
FILE: lm/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - backend_config.ArcLmBackend
    - backend_config.ArcLmBackendConfig
    - backend_config.build_arc_lm_backend
    - backend_config.logger
    - backend_transformers.TransformersArcLmBackend
    - backend_unsloth.UnslothArcLmBackend
    - backend_unsloth.logger
```

```
FILE: lm/backend_config.py
  Classes: (none)
  Functions: build_arc_lm_backend
  Imports (extracted):
    - layers.layer_0_core.level_0.get_logger
    - layers.layer_1_competition.level_0_infra.level_0.unsloth_available
    - layers.layer_1_competition.level_0_infra.level_3.LmBackend
    - layers.layer_1_competition.level_0_infra.level_3.LmBackendConfig
    - layers.layer_1_competition.level_0_infra.level_3.MockLmBackend
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3.UnslothArcLmBackend
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3.TransformersArcLmBackend
```

```
FILE: lm/backend_transformers.py
  Classes: TransformersArcLmBackend
  Functions: (none)
  Imports (extracted):
    - importlib
    - typing.Any
    - layers.layer_1_competition.level_0_infra.level_3.LmBackend
    - layers.layer_1_competition.level_0_infra.level_3.LmBackendConfig
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.ArcLmAdaptationConfig
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3.SharedTorchLmInference
```

```
FILE: lm/backend_unsloth.py
  Classes: UnslothArcLmBackend
  Functions: (none)
  Imports (extracted):
    - importlib
    - typing.Any
    - layers.layer_0_core.level_0.get_logger
    - layers.layer_1_competition.level_0_infra.level_0.load_adapter_state_dict
    - layers.layer_1_competition.level_0_infra.level_0.torch_dtype_from_config
    - layers.layer_1_competition.level_0_infra.level_0.unsloth_available
    - layers.layer_1_competition.level_0_infra.level_3.LmBackend
    - layers.layer_1_competition.level_0_infra.level_3.LmBackendConfig
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.ArcLmAdaptationConfig
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.COMMON_PEFT_PARAMS
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.get_peft_model_state_dict
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.set_peft_model_state_dict
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3.SharedTorchLmInference
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_4.lm_task_adaptation.run_unsloth_task_adaptation
```

```
FILE: lm_task_adaptation/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - runner.Grid
    - runner.logger
    - runner.run_unsloth_task_adaptation
```

```
FILE: lm_task_adaptation/runner.py
  Classes: (none)
  Functions: run_unsloth_task_adaptation
  Imports (extracted):
    - gc
    - importlib
    - io
    - tempfile
    - contextlib.redirect_stderr
    - contextlib.redirect_stdout
    - layers.layer_0_core.level_0.get_logger
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.UnslothFixedTrainer
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.ArcQwenGridChatFormatter
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.QwenDataCollatorForCompletionOnlyLM
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3.resolve_collator_token_ids
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3.build_task_training_rows
```

```
FILE: stages/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - train.logger
    - train.run_train_pipeline
    - tune.logger
    - tune.run_tune_pipeline
```

```
FILE: stages/train.py
  Classes: (none)
  Functions: run_train_pipeline
  Imports (extracted):
    - pathlib.Path
    - typing.Any
    - typing.Optional
    - layers.layer_0_core.level_0.ensure_dir
    - layers.layer_0_core.level_0.get_logger
    - layers.layer_0_core.level_4.save_json
    - layers.layer_1_competition.level_0_infra.level_0.contest_models_dir
    - layers.layer_1_competition.level_0_infra.level_1.RunContext
    - layers.layer_1_competition.level_0_infra.level_1.commit_run_artifacts
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.require_data_root
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.ARC26Paths
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.default_chosen_params
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3.get_trainer
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3.list_available_models
```

```
FILE: stages/tune.py
  Classes: (none)
  Functions: run_tune_pipeline
  Imports (extracted):
    - pathlib.Path
    - typing.Optional
    - layers.layer_0_core.level_0.ensure_dir
    - layers.layer_0_core.level_0.get_logger
    - layers.layer_0_core.level_4.save_json
    - layers.layer_1_competition.level_0_infra.level_0.contest_models_dir
    - layers.layer_1_competition.level_0_infra.level_1.RunContext
    - layers.layer_1_competition.level_0_infra.level_1.commit_run_artifacts
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.read_submit_max_tasks_env
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.default_chosen_params
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.get_per_model_entry
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.resolve_neural_paths_from_entry
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.ARC26Paths
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.require_data_root
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3.score_neural_on_evaluation
```

#### 3. Package Role (orchestrator summary)

- Tier **4** under `layers.layer_1_competition.level_1_impl.level_arc_agi_2`.

#### 4. Tests / notebooks

- (Not inventoried in this pass; see repo `tests/` / Kaggle notebooks if present.)

#### 5. Flags / static hints

- Precheck report: `precheck_level_arc_agi_2_level_4_2026-04-21.md` — machine precheck skipped (`torchvision` missing in runner env).

#### 6. Static scan summary

- Same as §5; full `audit_precheck.py` stack did not execute.
