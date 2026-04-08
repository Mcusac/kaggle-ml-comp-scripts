---
generated: 2026-04-08
audit_scope: contests_special
level_name: level_arc_agi_2_root
profile: full
run_mode: apply fixes (active overhaul)
artifact_kind: audit
---

# Audit: `level_arc_agi_2_root`

## Machine precheck

`dev/scripts/audit_precheck.py` **did not complete** in this environment: devtools import stack fails in `layer_0_core` vision models when `torch` is unavailable (`AttributeError: 'NoneType' object has no attribute 'Tensor'`). Treat machine Phase-7 reconciliation as **pending** until a venv with working `torch` (or a stubbed CI image) runs the script.

## Applied fixes (contest tree + integration tests)

### ARC contest package (`level_arc_agi_2/`)

No additional source edits were required in this pass beyond prior work: barrels and public LLM-TTA helpers in [`level_0`](c:\Users\mdc0431\OneDrive - UNT System\Documents\Kaggle\code\input\kaggle-ml-comp-scripts\scripts\layers\layer_1_competition\level_1_impl\level_arc_agi_2\level_0) / [`level_3/llm_tta_runner.py`](c:\Users\mdc0431\OneDrive - UNT System\Documents\Kaggle\code\input\kaggle-ml-comp-scripts\scripts\layers\layer_1_competition\level_1_impl\level_arc_agi_2\level_3\llm_tta_runner.py) already match `init-exports.mdc` and import-surface guidance.

### Devtools unit tests (wrong modules / wrong tiers)

[`test_arc_agi_2_llm_tta_dfs.py`](c:\Users\mdc0431\OneDrive - UNT System\Documents\Kaggle\code\input\kaggle-ml-comp-scripts\scripts\layers\layer_2_devtools\level_1_impl\tests\unit\test_contest\test_arc_agi_2_llm_tta_dfs.py) and [`test_arc_agi_2_validate_pipeline.py`](c:\Users\mdc0431\OneDrive - UNT System\Documents\Kaggle\code\input\kaggle-ml-comp-scripts\scripts\layers\layer_2_devtools\level_1_impl\tests\unit\test_contest\test_arc_agi_2_validate_pipeline.py) referenced **non-existent or incorrect** import paths:

| Issue | Correction |
|--------|------------|
| `level_1.augmentations` / `decoder_dfs` / `candidate_scoring` | Modules live under **`level_0`**; switched to `…level_0` barrel imports. |
| `level_2.llm_tta_inference` | `LlmTtaDfsConfig` lives in **`level_0`**; switched to `…level_0`. |
| `level_4.stages` | No `stages` under `level_4`; submission/train stages live under **`level_5`** (`run_submission_pipeline`, `run_train_pipeline`). |
| `level_5.orchestration` | No `orchestration` package under `level_5`; pipeline façades are in **`level_6`** (`run_validate_data_pipeline`, `run_train_pipeline_result`, `run_train_and_submit_pipeline_result`). |
| Monkeypatch target for `run_train_pipeline` | Updated to `…level_5.stages.run_train_pipeline`. |
| `level_0.heuristics` only for barrel symbol | `predict_attempts_from_chosen_params` imported from **`level_0`** barrel. |

These tests validate the contest package; fixing them aligns with [`python-import-surfaces.mdc`](c:\Users\mdc0431\OneDrive - UNT System\Documents\Kaggle\code\input\kaggle-ml-comp-scripts\.cursor\rules\python-import-surfaces.mdc) and the actual on-disk layout.

## Verification

From `input/kaggle-ml-comp-scripts/scripts` (with working framework imports):

```text
pytest layers/layer_2_devtools/level_1_impl/tests/unit/test_contest/test_arc_agi_2_llm_tta_dfs.py layers/layer_2_devtools/level_1_impl/tests/unit/test_contest/test_arc_agi_2_validate_pipeline.py
```

## Follow-ups

- Re-run `audit_precheck.py` for `contests_special` / `level_arc_agi_2_root` once the devtools → `layer_0_core` import chain runs without optional-dep failures.
- Optional: scan other contest tests for the same `level_4.stages` / wrong-tier patterns (this pass scoped to `level_arc_agi_2` test files only).
