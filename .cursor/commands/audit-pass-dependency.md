# audit-pass-dependency

**Pass:** dependency direction and import graph sanity.

## Agent instructions

1. Read `.cursor/rules/code-audit-delegation.mdc` and delegate with **`Task(subagent_type="code-audit", …)`**.
2. Embed the user’s **entire** chat message (including `@` paths) inside the Task prompt as a quoted **`USER_REQUEST`** block — verbatim.
3. Tags for appended summaries: [audit-pass-tags.md](audit-pass-tags.md).

## User request template (paste and customize)

```text
USER_REQUEST (verbatim for Task body):

"""
audit pass: dependency-direction

TARGET:
@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_0_infra

profile imports
recommendations only
no code edits

OPTIONAL — reference journal (append a short summary section here after canonical audit artifacts):
REFERENCE_DOC: .cursor/audit-results/competition_infra/summaries/run2_level_0_infra_classification_<DATE>_v<N>.md

PASS FOCUS (orchestrator still runs full planner+auditor per policy; auditor emphasizes):
- Imports from higher layers / wrong direction for this tree
- Circular dependencies within the target scope
- Cross-layer leakage (tag per audit-pass-tags.md)
- Infra must not depend on contest implementation packages incorrectly
- Reconcile machine precheck import hints in the audit (Phase 7)

OUTPUT TAGS: use # VIOLATION: dependency — ... from input/kaggle-ml-comp-scripts/.cursor/commands/audit-pass-tags.md
"""
```

## Examples

**Infra tier only:**

```text
audit level_0_infra/level_1 profile imports
recommendations only
@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_0_infra/level_1
```

**General level:**

```text
audit level_3 profile imports
recommendations only
```

**Impl root:**

```text
audit pass: dependency-direction
profile imports
recommendations only
@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_1_impl
```

## Canonical outputs

Per target: `.cursor/audit-results/<scope>/inventories/INVENTORY_<level_name>.md` and `audits/<level_name>_audit.md`.

See hub: [audit-pass.md](audit-pass.md).

This command will be available in chat with /audit-pass-dependency
