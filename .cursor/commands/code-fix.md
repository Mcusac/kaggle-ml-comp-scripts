# code-fix

Apply structured fixes after **`/code-audit`** (or ad-hoc) using **deterministic tools first**, then **minimal manual edits**. This is separate from the audit pipeline: audits stay **review + recommendations**; `/code-fix` is the optional apply phase.

**Orchestrator:** `.cursor/agents/code-fix.md`  
**Planner:** `.cursor/agents/code-fix-planner.md`  
**Executor (runner):** `.cursor/agents/code-fix-runner.md`  
*(Legacy label **doer** → `.cursor/agents/code-fix-doer.md` redirects to the runner.)*

**Delegation:** embed the user message as a verbatim **`USER_REQUEST`** block. **Rule file:** `.cursor/rules/code-fix-delegation.mdc`

**Copy-paste templates** (also in `input/kaggle-ml-comp-scripts/.cursor/commands/code-audit-quick-reference.md` → *Subagent `Task` templates*):

Replace **`<TARGET>`** with your `@` path (under `scripts/layers/...`).

### `Task(subagent_type="code-fix")` — apply audit recommendations

```text
Delegate Task(subagent_type="code-fix") with:

USER_REQUEST (verbatim):

"""
apply recommendations
profile full

@<TARGET>
"""
```

### `Task(subagent_type="code-fix")` — lite (init regen only)

```text
Delegate Task(subagent_type="code-fix") with:

USER_REQUEST (verbatim):

"""
tools: init regen

@<TARGET>
"""
```

## When to use

- After **`/code-audit`** with `recommendations only`: run `/code-fix` with the same `@` target to apply tool-first fixes and record a run summary.
- After a **machine run** (e.g. **`code-audit-runner`** + **`code-audit-analyzer`**): you may paste the analyzer’s **structured findings** into the **`/code-fix`** request (or an extra `analyzer_findings` block) so **`code-fix-planner`** can prioritize; the orchestrator still runs **planner** then **`code-fix-runner`**.
- **Lite run:** you know what changed; pass explicit lines such as `tools: init regen` and the `@` path — no prior audit required.

## Default behavior

- **Tool-first:** e.g. `__init__.py` / barrel drift → `regenerate_package_inits.py --fix` (from `scripts/` cwd). Manual edits only for what tools cannot cover.
- **Prefer fix pipeline for multi-step tool runs:** when you want a deterministic “bundle” of tool-first fixes with one summary artifact, use:\n+\n+  `python -m layers.layer_2_devtools.level_1_impl.level_2.run_code_fix_pipeline --help`\n+\n+  It emits a single `FIX_RUN_*.md` under `.cursor/audit-results/<scope>/summaries/`.
- **Artifacts:** write `FIX_RUN_<level_or_slug>_<YYYY-MM-DD>.md` under  
  `input/kaggle-ml-comp-scripts/.cursor/audit-results/<scope>/summaries/`  
  (same scope convention as audits — see `code-audit-reference.md` Step 1b for `audit_scope`).

## Example requests

**Apply audit recommendations for a contest tree:**

```text
/code-fix
apply recommendations
profile full

@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_1_impl/level_arc_agi_2
```

**Lite: only regenerate inits:**

```text
/code-fix
tools: init regen

@input/kaggle-ml-comp-scripts/scripts/layers/layer_1_competition/level_1_impl/level_arc_agi_2
```

**Dry check (no writes) — use the tool’s flags via planner/runner:** prefer documenting `--dry-run` on init regen before `--fix`.

## Init regeneration command (reference)

From `input/kaggle-ml-comp-scripts/scripts`:

```bash
python layers/layer_2_devtools/level_1_impl/level_2/regenerate_package_inits.py --root layers/... --fix
```

One shell command per line on Windows PowerShell 5.x (no `&&`).

This command will be available in chat with /code-fix
