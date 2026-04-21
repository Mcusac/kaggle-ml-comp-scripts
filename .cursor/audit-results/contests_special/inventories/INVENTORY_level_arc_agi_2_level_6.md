---
generated: 2026-04-21
audit_scope: contests_special
level_name: level_arc_agi_2_level_6
pass_number: 1
run_id: arc-agi-2-full-recommendations
artifact_kind: inventory
audit_profile: full
---

### INVENTORY: `level_arc_agi_2_level_6`

#### 1. Package & File Tree

```
__init__.py [__init__.py]
  __init__.cpython-311.pyc
  arc_contest_pipeline.cpython-311.pyc
  handlers.cpython-311.pyc
  orchestration.cpython-311.pyc
  single_stage.cpython-311.pyc
dispatch/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    submit_strategy_dispatch.cpython-311.pyc
  submit_strategy_dispatch.py
single_stage.py
```

#### 2. Per-File Details

```
FILE: __init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - dispatch
    - dispatch.*
```

```
FILE: dispatch/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - submit_strategy_dispatch.logger
    - submit_strategy_dispatch.predict_attempts_for_submit_strategy
```

```
FILE: dispatch/submit_strategy_dispatch.py
  Classes: (none)
  Functions: predict_attempts_for_submit_strategy
  Imports (extracted):
    - typing.Any
    - typing.Mapping
    - layers.layer_0_core.level_0.get_logger
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.predict_attempts_from_chosen_params
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.stack_raise_if_unsupported_strategy
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.LlmTtaDfsConfig
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_5.predict_attempts_for_llm_tta_dfs
```

```
FILE: single_stage.py
  Classes: (none)
  Functions: run_train_pipeline_result, run_tune_pipeline_result, run_submission_pipeline_result
  Imports (extracted):
    - typing.Optional
    - layers.layer_0_core.level_0.PipelineResult
    - layers.layer_0_core.level_1.run_pipeline_result_with_validation_first
    - layers.layer_1_competition.level_0_infra.level_0.capture_config_paths
    - layers.layer_1_competition.level_0_infra.level_0.capture_submission_paths
    - layers.layer_1_competition.level_0_infra.level_1.RunContext
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3.run_validate_data_pipeline
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_4.run_train_pipeline
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_4.run_tune_pipeline
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_5.run_submission_pipeline
```

#### 3. Package Role (orchestrator summary)

- Tier **6** under `layers.layer_1_competition.level_1_impl.level_arc_agi_2`.

#### 4. Tests / notebooks

- (Not inventoried in this pass; see repo `tests/` / Kaggle notebooks if present.)

#### 5. Flags / static hints

- Precheck report: `precheck_level_arc_agi_2_level_6_2026-04-21.md` — machine precheck skipped (`torchvision` missing in runner env).

#### 6. Static scan summary

- Same as §5; full `audit_precheck.py` stack did not execute.
