# audit-pass-classify

**Pass:** classify modules/symbols (placement, generic vs contest-specific, decomposition hints).

## Agent instructions

1. Code-audit per `.cursor/rules/code-audit-delegation.mdc` (canonical: planner/auditor `Task`s; legacy: **`Task(code-audit)`**); verbatim **`USER_REQUEST`**.
2. Use **`audit_profile: full`** unless the user overrides.
3. In the auditor result and optional `REFERENCE_DOC` appendix, use the **(1)–(6)** legend and `# CANDIDATE:` / `# VIOLATION:` tags from [audit-pass-tags.md](audit-pass-tags.md).

## User request template

```text
USER_REQUEST (verbatim):

"""
audit pass: classify

TARGET:
@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_0_infra

profile full
recommendations only
no code edits

REFERENCE_DOC (optional):
.cursor/audit-results/competition_infra/summaries/run2_level_0_infra_classification_<DATE>_v<N>.md

CLASSIFY each notable module/symbol as:
(1) competition-specific infra — VALID here
(2) generic utility — should move to layer_0_core
(3) thin wrapper around layer_0_core
(4) duplicate / near-duplicate of layer_0_core
(5) overly high-level orchestration — consider higher layer
(6) mixed responsibility — decompose

DECOMPOSITION: for (6), suggest focused submodules and orchestration vs implementation split.

FLAGS: copy tag lines from input/kaggle-ml-comp-scripts/.cursor/commands/audit-pass-tags.md
"""
```

## Examples

**Infra full tree:** attach `@.../level_0_infra` and use template above.

**Single contest implementation package:**

```text
audit pass: classify
profile full
recommendations only
@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_1_impl/level_csiro
```

Hub: [audit-pass.md](audit-pass.md) · Targets: [audit-targets.md](audit-targets.md).

This command will be available in chat with /audit-pass-classify
