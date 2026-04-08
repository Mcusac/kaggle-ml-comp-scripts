# audit-pass-validate

**Pass:** post-change validation — **no edits**.

## Agent instructions

1. **`Task(subagent_type="code-audit", …)`**, verbatim **`USER_REQUEST`**.
2. Use **`profile imports`** first for fast regression on layering; add **`profile full`** if the user wants a full pass.
3. **`recommendations only`** / **`no code edits`** required.
4. Report **`# REGRESSION: ...`** tags from [audit-pass-tags.md](audit-pass-tags.md) when prior fixes appear undone.

## User request template

```text
USER_REQUEST (verbatim):

"""
audit pass: post-cleanup-validation

TARGET:
@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_0_infra

profile imports
recommendations only
no code edits

OPTIONAL second sweep in same request:
then audit same TARGET profile full recommendations only no code edits

REFERENCE_DOC:
.cursor/audit-results/competition_infra/summaries/run2_level_0_infra_classification_<DATE>_v<N>.md

VERIFY vs REFERENCE_DOC / prior apply pass:
- No disallowed wrappers returned (except intentional barrels)
- No reintroduced duplication vs layer_0_core where previously fixed
- Inline IO policy status
- Registry centralization status
- Dependency rules

TAG regressions: # REGRESSION: ... per audit-pass-tags.md
APPEND summary section to REFERENCE_DOC
"""
```

## Examples

```text
audit pass: post-cleanup-validation
profile imports
recommendations only
no code edits
@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_1_impl
```

Hub: [audit-pass.md](audit-pass.md).

This command will be available in chat with /audit-pass-validate
