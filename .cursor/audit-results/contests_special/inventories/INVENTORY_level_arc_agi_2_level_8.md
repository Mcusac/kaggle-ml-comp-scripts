---
generated: 2026-04-21
audit_scope: contests_special
level_name: level_arc_agi_2_level_8
pass_number: 1
run_id: arc-agi-2-full-recommendations
artifact_kind: inventory
audit_profile: full
---

### INVENTORY: `level_arc_agi_2_level_8`

#### 1. Package & File Tree

```
__init__.py [__init__.py]
  __init__.cpython-311.pyc
handlers/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    pipeline_handlers.cpython-311.pyc
    registry.cpython-311.pyc
  pipeline_handlers.py
```

#### 2. Per-File Details

```
FILE: __init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - handlers
    - handlers.*
```

```
FILE: handlers/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - pipeline_handlers.submit
    - pipeline_handlers.train
    - pipeline_handlers.train_and_submit
    - pipeline_handlers.tune
    - pipeline_handlers.tune_and_submit
    - pipeline_handlers.validate_data
```

```
FILE: handlers/pipeline_handlers.py
  Classes: (none)
  Functions: validate_data, train, tune, submit, train_and_submit, tune_and_submit
  Imports (extracted):
    - argparse
    - layers.layer_1_competition.level_0_infra.level_0.llm_tta_kwargs_from_args
    - layers.layer_1_competition.level_0_infra.level_0.log_result
    - layers.layer_1_competition.level_0_infra.level_1.parse_models_csv
    - layers.layer_1_competition.level_0_infra.level_1.resolve_data_root_from_args
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.init_run_context
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.run_validate_data_pipeline
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_6.run_submission_pipeline_result
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_6.run_train_pipeline_result
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_6.run_tune_pipeline_result
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_7.run_train_and_submit_pipeline_result
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_7.run_tune_and_submit_pipeline_result
```

#### 3. Package Role (orchestrator summary)

- Tier **8** under `layers.layer_1_competition.level_1_impl.level_arc_agi_2`.

#### 4. Tests / notebooks

- (Not inventoried in this pass; see repo `tests/` / Kaggle notebooks if present.)

#### 5. Flags / static hints

- Precheck report: `precheck_level_arc_agi_2_level_8_2026-04-21.md` — machine precheck skipped (`torchvision` missing in runner env).

#### 6. Static scan summary

- Same as §5; full `audit_precheck.py` stack did not execute.
