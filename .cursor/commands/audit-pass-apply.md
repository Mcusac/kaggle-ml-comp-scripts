# audit-pass-apply

**Pass:** implement fixes from a prior campaign — **edits allowed**.

## Agent instructions

1. Code-audit per `.cursor/rules/code-audit-delegation.mdc` (canonical: planner/auditor `Task`s; legacy: **`Task(code-audit)`**); verbatim **`USER_REQUEST`**.
2. **`USER_REQUEST` MUST include apply-fix language** so orchestrator sets **`run_mode: default`** (e.g. **`apply fixes`**, **`active overhaul`**, **`run_mode default`**) — see `.cursor/agents/code-audit-orchestrator-details.md` Step 1c.
3. **`audit_profile: full`** unless the change set is import-only (`profile imports`).
4. Orchestrator guardrails: do not delete/move files under `scripts/layers/` **unless** the user explicitly asked cleanup; follow auditor Phase 8 for caller updates when APIs change.
5. Append **completed items** / change summary to `REFERENCE_DOC` if provided.

## User request template

```text
USER_REQUEST (verbatim):

"""
audit pass: apply-fixes-from-reference

apply fixes
active overhaul

TARGET:
@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_0_infra

profile full

REFERENCE_DOC (source of truth for what to implement):
.cursor/audit-results/competition_infra/summaries/run2_level_0_infra_classification_<DATE>_v<N>.md

ORDER (prefer this sequence):
1. Dependency violations
2. Remove thin wrappers (non-barrel) where safe
3. Replace duplicated logic
4. Move generic utilities toward layer_0_core when agreed in REFERENCE_DOC
5. Extract inline IO
6. Consolidate registries incrementally
7. Decompose mixed modules per REFERENCE_DOC
8. Update imports / callers (Phase 8)

After edits: list files touched and mark REFERENCE_DOC sections completed.
"""
```

## Safety

- Prefer **incremental** PR-sized steps; user may add **`incremental only`** phrases only if they intend orchestrator **artifact_policy: incremental_only** (see Step 0.7).

Hub: [audit-pass.md](audit-pass.md). Follow-up: [audit-pass-validate.md](audit-pass-validate.md).

This command will be available in chat with /audit-pass-apply
