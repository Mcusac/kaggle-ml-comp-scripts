---
generated: 2026-04-21
audit_scope: contests_special
level_name: level_arc_agi_2_root
pass_number: 1
run_id: arc-agi-2-full-recommendations
artifact_kind: inventory
audit_profile: full
---

### INVENTORY: `level_arc_agi_2_root`

#### 1. Package & File Tree

```
__init__.py [__init__.py]
_run12_argv_before.txt
level_0/
level_1/
level_2/
level_3/
level_4/
level_5/
level_6/
level_7/
level_8/
registration.py
```

#### 2. Per-File Details

```
FILE: __init__.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - level_0
    - level_1
    - level_2
    - level_3
    - level_4
    - level_5
    - level_6
    - level_7
    - level_8
    - level_0.*
    - level_1.*
    - level_2.*
    - level_3.*
    - level_4.*
    - level_5.*
    - level_6.*
    - level_7.*
    - level_8.*
```

```
FILE: registration.py
  Classes: (none)
  Functions: (none)
  Imports (extracted):
    - layers.layer_1_competition.level_0_infra.level_1.register_contest
    - layers.layer_1_competition.level_0_infra.level_1.register_notebook_commands_module
    - layers.layer_1_competition.level_0_infra.level_2.register_cli_handlers_module
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.paths.ARC26Paths
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.config.ARC26Config
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.config.ARC26DataSchema
    - layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.config.ARC26PostProcessor
```

#### 3. Package Role (orchestrator summary)

- Tier **0** under `layers.layer_1_competition.level_1_impl.level_arc_agi_2`.

#### 4. Tests / notebooks

- (Not inventoried in this pass; see repo `tests/` / Kaggle notebooks if present.)

#### 5. Flags / static hints

- Precheck report: `precheck_level_arc_agi_2_root_2026-04-21.md` — machine precheck skipped (`torchvision` missing in runner env).

#### 6. Static scan summary

- Same as §5; full `audit_precheck.py` stack did not execute.
