---
generated: 2026-04-21
audit_scope: contests_special
level_name: level_arc_agi_2_level_5
pass_number: 1
run_id: arc-agi-2-full-recommendations
artifact_kind: inventory
audit_profile: full
---

### INVENTORY: `level_arc_agi_2_level_5`

#### 1. Package & File Tree

```
__init__.py [__init__.py]
  __init__.cpython-311.pyc
  arc_contest_pipeline.cpython-311.pyc
  orchestration.cpython-311.pyc
  runner.cpython-311.pyc
  stages.cpython-311.pyc
  submit.cpython-311.pyc
runner.py
```

#### 2. Per-File Details

```
FILE: __init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - runner.Grid
    - runner.logger
    - runner.predict_attempts_for_llm_tta_dfs
```

```
FILE: runner.py
  Classes: (none)
  Functions: predict_attempts_for_llm_tta_dfs
  Imports (extracted):
    - time
    - typing.Any
    - typing.Mapping
    - layers.layer_0_core.level_0.get_logger
    - layers.layer_1_competition.level_0_infra.level_1.build_runtime_profile
    - layers.layer_1_competition.level_0_infra.level_1.prepare_artifact_layout
    - layers.layer_1_competition.level_0_infra.level_1.write_decoded_shard
    - layers.layer_1_competition.level_0_infra.level_1.write_intermediate_candidates
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.LlmTtaDfsConfig
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.apply_augmentation
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.apply_runtime_profile
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.build_budget
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.coerce_arc_grid
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.generate_augmentation_specs
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.invert_augmentation
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.llm_tta_augment_seed
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.llm_tta_grid_hw
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.predict_attempts_from_chosen_params
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.validate_llm_tta_dfs_config
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.CandidatePrediction
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.build_fallback_attempts
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.pick_ranked_attempts
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.decode_with_cell_probs
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.decode_with_support_grids
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.decode_with_turbo_lm
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_4.prepare_llm_tta_backend
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_4.restore_adapter_safely
```

#### 3. Package Role (orchestrator summary)

- Tier **5** under `layers.layer_1_competition.level_1_impl.level_arc_agi_2`.

#### 4. Tests / notebooks

- (Not inventoried in this pass; see repo `tests/` / Kaggle notebooks if present.)

#### 5. Flags / static hints

- Precheck report: `precheck_level_arc_agi_2_level_5_2026-04-21.md` — machine precheck skipped (`torchvision` missing in runner env).

#### 6. Static scan summary

- Same as §5; full `audit_precheck.py` stack did not execute.
