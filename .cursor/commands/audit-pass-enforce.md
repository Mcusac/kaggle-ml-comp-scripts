# audit-pass-enforce

**Pass:** layer thickness, inline I/O, registry duplication — **findings only** (no edits).

## Agent instructions

1. **`Task(subagent_type="code-audit", …)`**, verbatim **`USER_REQUEST`**.
2. **`audit_profile: full`**. Ensure **`run_mode`** stays **recommendations-only** (user must not say apply fixes on this pass).
3. Map findings to `# VIOLATION: infra-too-thick`, `# VIOLATION: inline-io`, `# VIOLATION: registry-duplication`, `# CANDIDATE: push-down-to-core` as appropriate — [audit-pass-tags.md](audit-pass-tags.md).

## User request template

```text
USER_REQUEST (verbatim):

"""
audit pass: enforce-responsibility

TARGET:
@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_0_infra

profile full
recommendations only
no code edits
report-only

REFERENCE_DOC (optional):
.cursor/audit-results/competition_infra/summaries/run2_level_0_infra_classification_<DATE>_v<N>.md

EVALUATE:
- Reusable logic trapped in infra vs belongs in layer_0_core
- Orchestration mixed with heavy implementation
- Large / thick modules
- Excessive non-barrel wrappers
- Multiple registry patterns overlapping
- Inline file I/O vs centralized IO helpers

TAG: per input/kaggle-ml-comp-scripts/.cursor/commands/audit-pass-tags.md
"""
```

## Examples

```text
audit pass: enforce-responsibility
profile full
recommendations only
@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_1_impl
```

Hub: [audit-pass.md](audit-pass.md).

This command will be available in chat with /audit-pass-enforce
