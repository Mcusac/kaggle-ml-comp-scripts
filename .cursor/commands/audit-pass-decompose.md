# audit-pass-decompose

**Pass:** mixed-responsibility modules — SRP splits, helper extraction, thin orchestration.

## Agent instructions

1. **`Task(subagent_type="code-audit", …)`**, verbatim **`USER_REQUEST`**.
2. **`audit_profile: full`** (Phases 1–3 emphasis).
3. Use `# CANDIDATE: decompose — ...` tags from [audit-pass-tags.md](audit-pass-tags.md).

## User request template

```text
USER_REQUEST (verbatim):

"""
audit pass: decompose

TARGET:
@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_0_infra

profile full
recommendations only
no code edits

REFERENCE_DOC (optional):
.cursor/audit-results/competition_infra/summaries/run2_level_0_infra_classification_<DATE>_v<N>.md

SCOPE:
- Prefer modules already marked (6) mixed-responsibility in REFERENCE_DOC; otherwise enumerate largest / most coupled modules in TARGET.

DELIVERABLES per flagged module:
- logical submodules
- helper boundaries
- orchestration vs implementation split

TAG: # CANDIDATE: decompose — ... per audit-pass-tags.md
"""
```

## Examples

```text
audit pass: decompose
profile full
recommendations only
@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_0_infra/level_3/submission
```

Hub: [audit-pass.md](audit-pass.md).

This command will be available in chat with /audit-pass-decompose
