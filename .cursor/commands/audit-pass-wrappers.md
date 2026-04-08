# audit-pass-wrappers

**Pass:** thin wrappers vs intentional **barrel** (`__init__.py`) surfaces.

## Agent instructions

1. **`Task(subagent_type="code-audit", …)`** with verbatim **`USER_REQUEST`**.
2. Use **`profile barrels`** (primary). User may request **`profile full`** if wrappers live next to non-barrel issues.
3. Enforce: `__init__.py` aggregation per `input/kaggle-ml-comp-scripts/.cursor/rules/python-import-surfaces.mdc` is **valid** — do not flag as `# VIOLATION: wrapper — no added value` unless policy is violated.
4. Flag logic modules that only delegate with no added behavior using tags from [audit-pass-tags.md](audit-pass-tags.md).

## User request template

```text
USER_REQUEST (verbatim):

"""
audit pass: thin-wrappers

TARGET:
@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_0_infra

profile barrels
recommendations only
no code edits

REFERENCE_DOC (optional):
.cursor/audit-results/competition_infra/summaries/run2_level_0_infra_classification_<DATE>_v<N>.md

FOCUS:
- Non-__init__ one-line delegation, pass-through only, rename-only wrappers
- Legitimate barrels: note with # NOTE: barrel — intentional re-export where applicable

SELECTION (optional): flagged-only list from REFERENCE_DOC instead of rescanning everything
"""
```

## Examples

```text
audit pass: thin-wrappers
profile barrels
recommendations only
@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_1_impl
```

Hub: [audit-pass.md](audit-pass.md).

This command will be available in chat with /audit-pass-wrappers
