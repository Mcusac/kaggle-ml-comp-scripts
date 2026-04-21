# audit-pass-duplicate

**Pass:** DRY — compare target code against **lower** layers for duplicates and near-duplicates.

## Agent instructions

1. Code-audit per `.cursor/rules/code-audit-delegation.mdc` (canonical: planner/auditor `Task`s; legacy: **`Task(code-audit)`**) + verbatim **`USER_REQUEST`**.
2. Default **`audit_profile: full`**. If the user only needs import-level DRY signals, they may say **`profile imports`**.
3. Auditor Phase 7b (DRY across levels) is central; ground-truth remains reading source in `layer_0_core` / infra as named in `USER_REQUEST`.
4. Tag with `# VIOLATION: DRY — ...` from [audit-pass-tags.md](audit-pass-tags.md).

## User request template

```text
USER_REQUEST (verbatim):

"""
audit pass: duplicate-detection

TARGET:
@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_0_infra

LOWER_ROOTS_FOR_COMPARISON:
@input/kaggle-ml-comp-scripts/scripts/layers/layer_0_core
@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_0_infra

profile full
recommendations only
no code edits

SELECTION (optional):
- full-rescan of TARGET, or
- flagged-only: only modules/symbols listed in REFERENCE_DOC from a prior classify pass

REFERENCE_DOC (optional):
.cursor/audit-results/competition_infra/summaries/run2_level_0_infra_classification_<DATE>_v<N>.md

FIND: exact duplicates, renamed duplicates, partially modified copies, reimplemented helpers vs LOWER_ROOTS.
TAG: # VIOLATION: DRY — duplicated from layer_0_core (or appropriate) per audit-pass-tags.md
"""
```

## Examples

**Impl vs core + infra:**

```text
audit pass: duplicate-detection
profile full
recommendations only
TARGET @input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_1_impl/level_cafa
COMPARE @input/kaggle-ml-comp-scripts/scripts/layers/layer_0_core
COMPARE @input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_0_infra
```

Hub: [audit-pass.md](audit-pass.md).

This command will be available in chat with /audit-pass-duplicate
