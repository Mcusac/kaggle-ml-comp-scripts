---
generated: 2026-04-21
audit_scope: contests_special
level_name: level_arc_agi_2_level_7
pass_number: 1
run_id: arc-agi-2-full-recommendations
artifact_kind: inventory
audit_profile: full
---

### INVENTORY: `level_arc_agi_2_level_7`

#### 1. Package & File Tree

```
__init__.py [__init__.py]
  __init__.cpython-311.pyc
  handlers.cpython-311.pyc
  submit.cpython-311.pyc
orchestration/
  __init__.py [__init__.py]
    __init__.cpython-311.pyc
    composites.cpython-311.pyc
    single_stage.cpython-311.pyc
  composites.py
submit.py
```

#### 2. Per-File Details

```
FILE: __init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - orchestration
    - orchestration.*
```

```
FILE: orchestration/__init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - composites.run_train_and_submit_pipeline_result
    - composites.run_tune_and_submit_pipeline_result
```

```
FILE: orchestration/composites.py
  Classes: (none)
  Functions: run_train_and_submit_pipeline_result, run_tune_and_submit_pipeline_result
  Imports (extracted):
    - typing.Optional
    - layers.layer_0_core.level_0.PipelineResult
    - layers.layer_1_competition.level_0_infra.level_0.ArtifactKeys
    - layers.layer_1_competition.level_0_infra.level_1.TwoStageValidateFirstPipelineResultShell
    - layers.layer_1_competition.level_0_infra.level_1.ValidateTrainSubmitPipelineResultShell
    - layers.layer_1_competition.level_0_infra.level_1.run_two_stage_pipeline_result_with_validation_first
    - layers.layer_1_competition.level_0_infra.level_1.RunContext
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3.run_validate_data_pipeline
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_6.run_submission_pipeline_result
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_6.run_train_pipeline_result
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_6.run_tune_pipeline_result
```

```
FILE: submit.py
  Classes: (none)
  Functions: run_submission_pipeline
  Imports (extracted):
    - pathlib.Path
    - typing.Any
    - typing.Optional
    - layers.layer_0_core.level_0.get_logger
    - layers.layer_0_core.level_4.load_json_raw
    - layers.layer_0_core.level_4.save_json
    - layers.layer_1_competition.level_0_infra.level_1.RunContext
    - layers.layer_1_competition.level_0_infra.level_1.commit_run_artifacts
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.ARC26PostProcessor
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.arc_find_first_existing_file
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.infer_finalize_artifact_root
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.stack_raise_if_unsupported_strategy
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.TEST_CHALLENGE_NAMES
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.ARC26Paths
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.require_data_root
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.build_llm_tta_config
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.get_per_model_entry
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.resolve_chosen_params_for_submit
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.resolve_neural_paths_from_entry
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.second_attempt_grid
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.predict_grid_from_checkpoint
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.pipelines.score_submission.log_local_evaluation_score_optional
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_6.predict_attempts_for_submit_strategy
```

#### 3. Package Role (orchestrator summary)

- Tier **7** under `layers.layer_1_competition.level_1_impl.level_arc_agi_2`.

#### 4. Tests / notebooks

- (Not inventoried in this pass; see repo `tests/` / Kaggle notebooks if present.)

#### 5. Flags / static hints

- Precheck report: `precheck_level_arc_agi_2_level_7_2026-04-21.md` — machine precheck skipped (`torchvision` missing in runner env).

#### 6. Static scan summary

- Same as §5; full `audit_precheck.py` stack did not execute.
