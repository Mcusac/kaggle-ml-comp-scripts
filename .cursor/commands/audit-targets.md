# audit-targets

**Preset paths** for `input/kaggle-ml-comp-scripts` when building `USER_REQUEST` for `/code-audit` or `/audit-pass-*`. Replace workspace prefix if your clone root differs; paths are relative to the **workspace** that contains `input/kaggle-ml-comp-scripts`.

## Scripts working directory

Most audit tooling expects:

```text
cd "input/kaggle-ml-comp-scripts/scripts"
```

(one line; no `&&` on PowerShell 5.x)

## Competition infra (`audit_scope: competition_infra`)

**Root (all infra tiers on disk):**

```text
@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_0_infra
```

**Single infra tier** (example `level_2`):

```text
@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_0_infra/level_2
```

**`USER_REQUEST` token** (orchestrator maps to same paths):

```text
audit level_0_infra/level_2 profile imports
```

(Legacy alias: `audit level_C2`.)

## Implementation layer (`level_1_impl`)

**All contest implementations:**

```text
@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_1_impl
```

**Single contest package** (example `level_csiro`):

```text
@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_1_impl/level_csiro
```

Audits for contest tiers often use `audit_scope: contests_special` and names like `level_csiro_level_0`; see `.cursor/agents/code-audit-reference.md` Step 1b / 1e.

## Contests tree (alternate layout)

If the contest lives under `contests/`:

```text
@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/contests/<slug>
```

Example:

```text
@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/contests/level_cafa
```

## General stack (`audit_scope: general`)

**Root:**

```text
@input/kaggle-ml-comp-scripts/scripts/layers/layer_0_core
```

**Single level** (example `level_5`):

```text
@input/kaggle-ml-comp-scripts/scripts/layers/layer_0_core/level_5
```

**`USER_REQUEST` token:**

```text
audit level_5 profile full
```

## Lower layers for duplicate passes

When a pass compares **target** vs **lower** code:

- **Core:** `@input/kaggle-ml-comp-scripts/scripts/layers/layer_0_core`
- **Infra (if auditing impl):** `@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_0_infra`

## Recommended composition

1. Copy preset paths from this file into your chat.
2. Open the pass doc (e.g. [audit-pass-dependency.md](audit-pass-dependency.md)).
3. Paste the filled **`USER_REQUEST`** template and delegate **`Task(subagent_type="code-audit", …)`** per `.cursor/rules/code-audit-delegation.mdc`.

This command will be available in chat with /audit-targets
