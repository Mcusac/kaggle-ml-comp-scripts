# Code-audit orchestrator — policy, parsing, machine steps, summary

**Audience:** the `code-audit` orchestrator. Read this file **in full** before Step 0,
alongside **`code-audit-reference.md`**. Step **3** (planner/auditor delegation) lives in
**`code-audit.md`** so the primary agent file stays action-focused.

---

**Machine fast path (speed + reuse):** Do **not** re-derive the full Step 1e target
list from prose or memory. For **`audit_preset: comprehensive`** over the default
layers tree, your **first machine action** after metadata is **Step 1f** via
**`Task(subagent_type="code-audit-runner", …)`** →
`python -m layers.layer_2_devtools.level_1_impl.level_2.run_code_audit_pipeline` (cwd
`kaggle-ml-comp-scripts/scripts/`), with **`--no-precheck --no-general-scan --no-csiro-scan`**
so the orchestrator does not duplicate work before **Step 2.7** and **Step 3**. Default
artifact layout: **`artifact_base/.cursor/audit-results/general/summaries/machine_runs/<run_id>/manifest.json`**
and sibling **`audit_queue.json`** (unless `--output-dir` / `--manifest` / `--no-queue-file`
override). Iterate the queue JSON **`targets` array** in
order; use each row’s `level_path`, `level_name`, `audit_scope`, and
`precheck_kind` for Step 2.7. When delegating planner/auditor work, fill slots
from `.cursor/audit-templates/task-prompt-templates.md` instead of inventing new
prompt shapes each run. **Legacy:** a human or **`shell`** may run **`audit_targets.py`**
with `--write-manifest` under `.../summaries/`; canonical machine routing is
**`code-audit-runner`**, not generic shell for the unified pipeline. See
`.cursor/agents/code-audit-runner.md`. **Optional (non-canonical):** after a machine run,
**`Task(code-audit-analyzer, …)`** can summarize the resulting **`manifest.json`**
(`.cursor/agents/code-audit-analyzer.md` — **manifest-only**; does **not** replace Step 2.7
or Step 3). **Optional (non-canonical):** **`Task(code-verify-runner, …)`** re-runs
**`run_code_audit_pipeline`** with parity flags and a **new** `run_id`, then
deterministically compares the new v1 manifest to a **baseline** path (regression
if `overall_exit_code` increases or new `failed_steps` appear) — see
**`.cursor/agents/code-verify-runner.md`**.

---

<a id="step-0"></a>

## Step 0 — Parse, normalize, and preserve `USER_REQUEST`

At the **start** of every run:

1. **Record a verbatim `USER_REQUEST` block** — Quote the user’s full message
   (including `@` references). Do **not** substitute a shorter paraphrase that
   drops scopes, paths, or level names. Normalization below **adds** structure;
   it does not replace the raw request.

2. **Extract candidate targets** from that message:
   - Directory paths the user attached (`@` paths)
   - Tokens like `level_N`, `level_csiro`, legacy `level_C\d+` (competition infra alias), etc.
   - Phrases such as “all general levels”, “audit level_2”, “full stack”

3. **General stack (`level_0` … `level_10`):**
   - Match directory names with `level_(\d+)` only (`level_0` … `level_10`).
   - **Dedupe** and sort by numeric **N ascending**. **Ignore the order** the
     user listed.
   - Log once: e.g. `Normalized run order (general): level_0, level_1, …`
   - For phrases like “all general levels” / “audit everything” **in the
     general scope**, discover packages under
     `input/kaggle-ml-comp-scripts/scripts/layers/layer_0_core/` (see reference Step 1). Include **only**
     numeric `level_0`…`level_10`. **Exclude** `layers`, `level_Z`, and other
     non-level packages unless the user explicitly asked for those scopes.

4. **Other scopes** (`competition_infra`, `contests_special`):
  - Map targets using reference **Step 1b**. For **competition infra** (`audit_scope: competition_infra`),
    on-disk packages are `layer_1_competition/level_0_infra/level_N/`; Python imports are
    `layers.layer_1_competition.level_0_infra.level_N`. Audit artifacts use **`level_name` =
     `level_N`** (same basename as on disk). Order by **N** ascending.
   - For contest/special trees, follow user paths or sorted directory names
     under `layer_1_competition/contests/` (or other roots they name).
5. **Token vs path (disambiguation):**
   - **`level_CK`** (regex `^level_C\d+$`, e.g. `level_C2`, **legacy user alias**) →
     `audit_scope: competition_infra`, `level_name: level_{K}` (e.g. `level_2`),
    `level_path: …/layer_1_competition/level_0_infra/level_{K}/`.
  - **`@` path** ending in `…/level_0_infra/level_K` → same as competition infra target above.
   - Bare **`level_N`** (numeric only, e.g. `level_2`) → **general** stack under
     `layer_0_core/` only — never competition infra. Competition infra tier **K** is
    addressed with an explicit `level_0_infra/level_K` path, `audit competition infra`, or a
     legacy **`level_CK`** token.

6. **Gaps in the run:** If the user chose a **sparse** subset (e.g. only
   `level_0` and `level_2`), **warn once** that Phase 7 for `level_2` cannot use
   a `level_1` audit from this run — then **proceed**. Do **not** block on
   confirmation unless the user asked to stop on ambiguity.

7. **Artifact base (`artifact_base`):** When every `@` path and discovered target
   sits under `input/kaggle-ml-comp-scripts/`, set **`artifact_base`** to that
   **package directory** (the folder that contains `scripts/` and `.cursor/`).
   All machine prechecks, manifests, inventories, and audits must resolve under
   `artifact_base/.cursor/audit-results/<scope>/{inventories,audits,summaries}/`.
   Optional **`USER_REQUEST`** override: **`artifact_root: package`** (default
   for this tree) vs **`artifact_root: workspace`** (write under the enclosing
   multi-repo workspace `.cursor/` instead). Never split incremental “complete?”
   checks across two different roots.

8. **Non‑negotiable pipeline:** For **each** target in the normalized list you
   **must** run **Step 3a (planner) then Step 3b (auditor)** before moving to
   the next level — see **Step 0.7** (default: always regenerate artifacts; no
   skipping Step 3 because files already exist). **Forbidden shortcuts:**
   - Skipping the planner or auditing from memory without a complete inventory
   - Calling the auditor with a “summary of inventory” instead of the full
     artifact (see **Handoff integrity**)
   - Writing audits, inventories, or summaries only under `.cursor/audit-results/`
     **root** — valid paths are **only** under `.cursor/audit-results/<scope>/{inventories,audits,summaries}/` (reference Step 1b)
   - Collapsing the whole stack into a single ad-hoc review pass
   - Ending the run after Step 1f and/or Step 2.7 only because canonical
     `INVENTORY_*` / `*_audit.md` already exist — **forbidden** unless **Step 0.7
     `incremental_only`** applies
   - Satisfying Step 3 by running a **machine emit script** (e.g.
     `comprehensive_audit_emit.py`) **without** both **3a** and **3b** — **forbidden**
     unless **Step 0.8** machine-emit opt-in applies

---

<a id="step-05"></a>

## Step 0.5 — `audit_preset`, `audit_profile`, and comprehensive segments

### `audit_profile` (always set)

Parse `USER_REQUEST` (case-insensitive). First match wins:

| Phrase in `USER_REQUEST` | `audit_profile` |
|--------------------------|-----------------|
| `profile imports` or `profile: imports` | `imports` |
| `profile barrels` or `profile: barrels` | `barrels` |
| `profile docs` or `profile: docs` | `docs` |
| `profile full` or `profile: full` | `full` |
| *(none of the above)* | `full` |

Pass **`audit_profile`** to **both** planner and auditor on every Step 3 call.
Include it in inventory/audit metadata (see `.cursor/audit-results/README.md`).

### `audit_preset`

- **`comprehensive`** — if `USER_REQUEST` contains any of: `comprehensive`,
  `preset comprehensive`, `audit all scopes`, `full multi-scope`, `all scopes`
  (case-insensitive). This **expands** the run to **all segments** in reference Step 1e.
  If the user also named specific levels, **prefer expansion** and log once that
  those tokens were superseded by the comprehensive preset.
  **You must then run Step 1f** (canonical: **`code-audit-runner`**
  / `run_code_audit_pipeline` — see [Step 1f](#step-1f) below) and treat its queue JSON output as
  the authoritative target list and order (unless the machine step fails — then fall
  back to reference Step 1e and log the failure). Do not type out the full
  multi-segment queue in chat.
- **`single`** — default. Use normal Step 0 target normalization and reference **Step 1**
  (one `audit_scope` per run unless the user explicitly lists cross-scope
  targets).

### `audit_preset` echo

Pass **`audit_preset`** (`single` | `comprehensive`) to the auditor on every
Step 3b call for traceability in the audit result header.

---

<a id="step-06"></a>

## Step 0.6 — Precheck mode (`audit_precheck.py`)

Parse `USER_REQUEST` (case-insensitive). **Precedence:** `pin_path` overrides
running the script; `skip` means do not run (unless `pin_path` also applies —
then use the pinned file). **`pin_date`** adds `--date` when you do run.

| Condition | Mode | Behavior |
|-----------|------|----------|
| Explicit path to an existing `precheck_*.md`, or phrases `precheck path:`, `precheck file:`, `use precheck:` followed by a filesystem path | **`pin_path`** | **Do not** run `audit_precheck.py`. Set `precheck_report_path` to that file’s **absolute** path for **every** target in the run. Verify the file exists. |
| `skip precheck`, `no precheck`, `precheck off`, `without precheck` | **`skip`** | **Do not** run the script. Omit `precheck_report_path` unless **`pin_path`** also applies (then use the file). |
| `precheck date YYYY-MM-DD` or `precheck --date YYYY-MM-DD` (ISO date) | **`pin_date`** | When running the script (default mode), append `--date YYYY-MM-DD` so outputs match that **version** / snapshot date. |
| None of the above | **`run`** (default) | **Mandatory:** before each target’s Step 3a, run the precheck command in Step 2.7 (unless the shell cannot run — see Step 2.7). |

Log the resolved mode once per run: e.g. `Precheck mode: run | skip | pin_path | pin_date+run`.

---

<a id="step-07"></a>

## Step 0.7 — Artifact policy (default: regenerate / overwrite)

Parse `USER_REQUEST` (case-insensitive) for **incremental** intent. **First match**
among the phrases below sets **`artifact_policy: incremental_only`**; otherwise
**`artifact_policy: regenerate`** (default).

| `artifact_policy` | When | Orchestrator behavior |
|-------------------|------|-------------------------|
| **`regenerate`** *(default)* | No incremental phrase matched | For **every** target: run Step 2.7 (unless Step 0.6 skip/pin), then **Step 3a then 3b**. **Rewrite** the canonical files `INVENTORY_<level_name>.md` and `<level_name>_audit.md` (same paths under the correct `<scope>/` — overwrites prior content). **Do not** skip 3a/3b because matching files already exist. **Do not** treat “all targets already have inventory + audit on disk” as a completed audit run. |
| **`incremental_only`** | User asked to avoid redoing work (see phrases below) | You **may** skip Step 3a and/or 3b for a target **only when** `USER_REQUEST` explicitly allows it; log each skipped target and reason. Still run Step 2.7 if precheck mode is `run` and the user did not narrow to “precheck only.” |

**`incremental_only` completion rule:** Treat a target as “already complete” for skip purposes **only** if **both** exist under the **same** resolved **`artifact_base`**:

- `artifact_base/.cursor/audit-results/<audit_scope>/inventories/INVENTORY_<level_name>.md`
- `artifact_base/.cursor/audit-results/<audit_scope>/audits/<level_name>_audit.md`

Do **not** treat a different ancestor directory (e.g. multi-repo workspace vs package) as satisfying this pair. A `summaries/precheck_*.md` file **alone** does **not** count — especially if JSON/metadata shows `precheck_status: skipped_machine_script`.

**Resume without guessing:** Optional `USER_REQUEST` phrases: **`resume from level_N`**, **`resume from <level_name>`** — begin Step 2.7 / 3 from that queue index or `level_name` even when earlier tiers have files on disk (avoids false “done” after an artifact-root mismatch).

**Phrases that set `incremental_only`** (any one is enough):

- `incremental only`, `incremental mode`, `incremental audit`
- `skip targets that already have inventory and audit`, `skip existing artifacts`
- `verify artifacts only`, `verification only`, `check artifacts only`
- `precheck only`, `machine pass only`, `manifest and precheck only` (no planner/auditor unless user also asks for them)
- `do not rerun planner`, `do not rerun auditor`, `skip planner`, `skip auditor` *(interpret as allowing skip of that phase when artifacts exist — log clearly)*

**If ambiguous** (e.g. “fast audit” without the phrases above), use **`regenerate`**
and log once that the default policy applies.

---

<a id="step-08"></a>

## Step 0.8 — Subagent fidelity (planner + auditor required)

**Deterministic scripts and LLM subagents work together.** The orchestrator obtains
the target queue via **Step 1f** (canonical: **`code-audit-runner`**
/ `run_code_audit_pipeline`) and runs **`audit_precheck.py`** in **Step 2.7** per target. The **planner** and
**auditor** **should** consume those outputs (`precheck_report_path`, optional
`inventory_bootstrap.py` fragment per Step 2.7) while still producing work that
follows `code-audit-planner.md` and `code-audit-auditor.md` in full — scripts
**accelerate** listing and static flags; they do **not** replace phased audit
reasoning or package policy.

**Forbidden:** Using **any** script (including
`python -m layers.layer_2_devtools.level_1_impl.level_2.comprehensive_audit_emit`) to
**generate** canonical `INVENTORY_<level_name>.md` or `<level_name>_audit.md`
**without** invoking **`code-audit-planner`** then **`code-audit-auditor`** for
that target in **this** run. Templated markdown is **not** equivalent to Step 3.

**Machine-emit opt-in (replaces 3a/3b for that run):** Only if `USER_REQUEST`
contains one of: **`machine emit only`**, **`skeleton inventory only`**,
**`use emit script`** (case-insensitive). Log the mode in Step 4; do **not**
describe the run as a full spec-compliant planner/auditor audit.

**If nested `Task` subagents cannot run:** Report blocked targets and **fail** or
pause — **do not** substitute emit scripts, and **do not** simulate planner or auditor
output in-process — unless machine-emit opt-in applies. The remediation is to run
orchestration from the **main chat assistant** (e.g. **`/code-audit`** in Cursor) so it
can invoke **`Task(code-audit-planner)`** and **`Task(code-audit-auditor)`** directly,
or to hand off `USER_REQUEST` to that assistant. **Top-level orchestration may compose any
number of focused subagent `Task`s** (planner, auditor, `code-audit-runner`, `shell` for ad-hoc commands, etc.); the limitation
applies when a **subagent** (e.g. a single `Task(code-audit)`) tries to nest further
`Task` delegations underneath itself.

---

<a id="reference-discovery"></a>

## Reference — discovery, paths, comprehensive queue, handoff

**Read in full** before resolving targets or invoking subagents:

**`.cursor/agents/code-audit-reference.md`**

It contains **Step 1** (target discovery), **Step 1b** (scope folders and
`level_name` rules), **Step 1e** (comprehensive segment queue), and **Subagent
handoff integrity** (inventory and `prior_level_apis` rules). **`code-audit.md`**
is the orchestrator entry (Step 3 delegation); **this file** holds parsing,
policies, machine steps, and summary rules.

---

<a id="step-1c"></a>

## Step 1c — Run metadata (every run)

Before the first subagent call for a run, set:

- `generated` — ISO date `YYYY-MM-DD` (and time if useful)
- `run_id` — optional short label (e.g. `second-pass-imports`)
- `pass_number` — `1` for the first full sweep in this user request; increment
  only when the user explicitly asks to re-audit a level or you are doing an
  intentional second pass

**Pass identical `generated`, `run_id`, `pass_number`, `audit_scope`,
`level_name`, numeric `level_number` (N), `audit_profile`, and `audit_preset`**
to **both** planner and auditor for that level. A mismatched **N** corrupts Phase 7:
for **`general`**, N is the general-stack tier; for **`competition_infra`**, N is the
infra tier index (on-disk folder `level_N`).

**Pass to both planner and auditor** in the prompt so every saved markdown file
includes this metadata at the top (YAML frontmatter or `**Generated:**` /
`**Pass:**` — see `audit-results/README.md`).

### Run modes

**Precedence (case-insensitive):**

1. If `USER_REQUEST` contains **no-edits** language → **`run_mode: recommendations-only`**  
   *(any of: `recommendations only`, `no code edits`, `report-only`, `findings only`)*  
   If both no-edits and apply-fix phrases appear, **no-edits wins**; log the conflict once.

2. Else if `USER_REQUEST` contains **apply-fix** language → **`run_mode: default`**  
   *(any of: `apply fixes`, `active overhaul`, `run_mode default`, `implement fixes`,
   `edit the code`, `make the edits`, `fix the code`)*

3. Else → **`run_mode: recommendations-only`** *(default: documentation-first)*

| `run_mode` | Auditor behavior |
|------------|------------------|
| **`recommendations-only`** | Findings and **proposed** changes **without** applying repo edits. |
| **`default`** | Full 8-phase **active overhaul** (code edits + Phase 8 when applicable). |

**Pass `run_mode`** on every Step 3b call. Log once per run: e.g.
`run_mode: recommendations-only | default`.

---

<a id="step-1d"></a>

## Step 1d — Full sweep first, optional second pass after

- **Phase A — Full sweep:** Complete every target level in ascending order
  **once** before any optional re-audit. Log explicitly, e.g.
  `Auditing level_N (pass 1, full sweep)`.
- **Phase B — Revisit:** Only when the user asks or a level failed. If you
  re-audit `level_0` after finishing `level_5`, do **not** mislabel the work as
  a later level. Use the correct `level_name`, set `pass_number` ≥ 2, and
  include `generated` so outputs are not confused.

---

<a id="step-1f"></a>

## Step 1f — Machine target queue (`run_code_audit_pipeline` / `code-audit-runner`)

**Required** when **`audit_preset: comprehensive`** and the user’s scope is the
standard multi-segment layers sweep (e.g. `@…/scripts/layers` or equivalent).
**Strongly recommended** for any other large multi-target run.

**Canonical (orchestrated machine route):** Delegate **`Task(subagent_type="code-audit-runner", …)`**
(see `.cursor/agents/code-audit-runner.md` and the Runner block in
`.cursor/audit-templates/task-prompt-templates.md`). The runner runs **only**  
`python -m layers.layer_2_devtools.level_1_impl.level_2.run_code_audit_pipeline` from
`kaggle-ml-comp-scripts/scripts/`. For hands-off to Step 2.7 + Step 3 (no duplicate
precheck or stack scans in the pipeline), pass **`--no-precheck --no-general-scan --no-csiro-scan`**.
**Default** outputs: **`artifact_base/.cursor/audit-results/general/summaries/machine_runs/<run_id>/manifest.json`**
and sibling **`audit_queue.json`**. Use **`--workspace-root`**, **`--run-id`**, and optionally
`--output-dir` / `--manifest` to pin paths. Log once: `target_count` (from manifest
`queue_summary` or the JSON), manifest path, queue path, and **do not** paste all rows into chat.

**Legacy / implementation detail:** `audit_targets.py` is the underlying devtools
queue builder; a **saved** `--write-manifest` under `.../summaries/audit_queue_<run_id>.json`
is still valid if you already have that file, but **new** comprehensive orchestration
should use **`code-audit-runner`** so the run also records pipeline metadata in
`manifest.json`.

1. **Iterate the queue JSON** `targets` array **in order** for Step 2.7 and Step 3. Each object
   includes `audit_scope`, `level_name`, `level_path` (absolute),
   `level_number`, `segment_id`, `segment_index`, `target_index`, and
   **`precheck_kind`**.

The queue matches reference **Step 1e**. Use **`precheck_kind`** only for
debugging or to pass `--precheck-kind` to `audit_precheck.py` when auto mode
mis-fires; default precheck command omits it (**`auto`** handles contest tier,
contest root, and `layer_Z_unsorted`).

**Planner/auditor prompts:** Copy the blocks from
`.cursor/audit-templates/task-prompt-templates.md` and substitute paths from
the current `targets[i]` row plus `precheck_report_path` after Step 2.7.

---

<a id="step-2"></a>

## Step 2 — Initialize the context store

Create an in-memory context store keyed by **`level_name`** (unique string for
this segment, e.g. `level_3` or `level_csiro_level_2`). This store holds the
structured output of each completed audit so it can be passed to **later
targets in the same segment** during Phase 7.

```
context_store = {}
# After each target completes:
# context_store["<level_name>"] = auditor_result
```

**Per-segment reset:** When **`audit_preset` is `comprehensive`**, set
`context_store = {}` at the **start of each segment** (general, `competition_infra`, and
**each** contest package under `layer_1_competition/contests/`). Never carry `prior_level_apis`
across segments.

When serializing `prior_level_apis` for the auditor, use **clearly labeled**
blocks:

`=== PRIOR: <level_name> ===`

(one block per **earlier** target in **this** segment only). Do **not** merge
into one unlabeled narrative.

*(Subagent handoff integrity — full rules: `code-audit-reference.md`.)*

---

<a id="step-27"></a>

## Step 2.7 — Machine precheck (devtools) — default ON

**Unless Step 0.6 mode is `skip` or `pin_path`**, you **must** run precheck
**once per target** immediately **before that target’s Step 3a**, with cwd =
`input/kaggle-ml-comp-scripts/scripts` (or the repo’s `scripts/` directory that
contains `layers/`). Use a **single** terminal invocation per target (no `&&` on
PowerShell 5.x).

1. **Working directory:** `cd` to `scripts/` first.

2. **Command** (add `--date YYYY-MM-DD` when Step 0.6 **`pin_date`** was set):

   `python -m layers.layer_2_devtools.level_1_impl.level_2.audit_precheck --audit-scope <general|competition_infra|contests_special> --level-path "<absolute level_path for this target>" --level-name "<level_name>"`  
   Optional: `--workspace-root "<absolute artifact_base>"` when discovery must pin `input/kaggle-ml-comp-scripts` explicitly (defaults usually infer the package when `level_path` lies under it).  
   **CI / automation:** use `--strict` or set **`AUDIT_MACHINE_STRICT=1`** so a precheck **skip stub** (optional deps missing) exits **non-zero**; see `input/kaggle-ml-comp-scripts/.cursor/audit-results/README.md` and `scripts/layers/layer_2_devtools/README.md`.

   **`contests_special`:** `--precheck-kind` defaults to **`auto`**. The script
   infers **contest tier** (`.../contests/<slug>/level_K`), **contest package
   root** (direct child of `contests/` with top-level `*.py`), or **special
   tree** (`layer_Z_unsorted` / that `level_name`). JSON from Step 1f includes
   `precheck_kind` for traceability; you may pass  
   `--precheck-kind contest_tier|contest_root|special_tree` to match it
   explicitly when desired.

   **Full general-stack sweep** (only when `USER_REQUEST` asks for a stack-wide
   precheck without auditing each level in this pass):  
   `python -m layers.layer_2_devtools.level_1_impl.level_2.audit_precheck --audit-scope general --full-general-scan --level-name general_stack`  
   Normal per-level audits still use the per-target command above for each `level_path`.

3. **Output:** `artifact_base/.cursor/audit-results/<audit_scope>/summaries/precheck_<level_name>_<date>.md` (and `.json`), plus a copy under `.../runs/<date>/<level_name>/`. Pass the **absolute path** to the `.md` as **`precheck_report_path`** to planner (3a) and auditor (3b). Prefer the file **just written** by this run.

4. **`pin_path` mode:** Do **not** run the script. Pass the user’s pinned `.md`
   path as `precheck_report_path` (verify it exists).

5. **Failure:** If **`run`** or **`pin_date`** mode and the script **cannot** run
   (no Python, wrong cwd, missing **`artifact_base`** `.cursor/audit-results`): log
   **⚠️ PRECHECK SKIPPED (environment)** once per target, omit
   `precheck_report_path`, and **continue** the audit — do not abort the run.

6. **Optional inventory fragment:** You may also run  
   `python -m layers.layer_2_devtools.level_1_impl.level_2.inventory_bootstrap --level-path "<same level dir>" --output <path>`  
   and pass that path as **`inventory_bootstrap_path`** to the planner.

---

<a id="step-4"></a>

## Step 4 — Final summary

After all levels in the run have been audited, produce a consolidated summary
containing:

- The preserved **`USER_REQUEST`** (or pointer that it was honored)
- **`artifact_policy`** (`regenerate` | `incremental_only`) from Step 0.7
- **`run_mode`** (`recommendations-only` | `default`) from Step 1c
- **`audit_preset`** and **`audit_profile`** for the run
- Which targets (`level_name`) were audited and under which `audit_scope`
  (for `comprehensive`, group by segment)
- `generated` / `pass_number` for the run
- Total count of changes made across all phases and all levels (or findings only
  if recommendations-only)
- All dependency rule violations found, grouped by level
- All cross-level violations found, grouped by level
- **All caller files touched** across the run (repos-wide updates) when
  applicable
- Any items flagged for human review (design decisions, breaking API changes,
  ambiguous ownership of logic)

Save cross-cutting summaries under the appropriate
`.cursor/audit-results/<scope>/summaries/` when you produce a markdown file.

Present this summary clearly so it can be used as a handoff document.

---

<a id="guardrails"></a>

## Guardrails

- **Artifact policy:** Default **`regenerate`** (Step 0.7) — full Step 2.7 + 3a + 3b
  per target and overwrite canonical inventory/audit files. Do not invent
  “verification-only” or “skip if exists” behavior unless `USER_REQUEST` matches
  **incremental_only** phrases.
- **Subagent fidelity (Step 0.8):** Do **not** satisfy Step 3 by running
  `comprehensive_audit_emit.py` (or similar) **without** both planner and auditor
  subagents, unless `USER_REQUEST` uses machine-emit opt-in phrases.
- Never skip a level that appears earlier in the normalized order than another
  target in the same run. If level_2 is in the run but level_1 is not, note
  that Phase 7 for level_2 is incomplete relative to level_1.
- Never run levels in parallel. The cross-level phase depends on sequential,
  completed results.
- If the planner or auditor returns an error or incomplete result for a level,
  stop and report the failure before proceeding to the next level.
- Do not modify any package files yourself. All edits are made by the auditor
  subagent (unless `run_mode` is recommendations-only). Your role is
  coordination, **USER_REQUEST** preservation, normalization, context passing,
  and path verification.
- **Package tree (layers):** Do **not** delete, move, or rename files under  
  `input/kaggle-ml-comp-scripts/scripts/layers/` during an audit run unless the
  user explicitly asked for that cleanup. Misplaced `INVENTORY_*.md` or other
  artifacts inside a level package → **report in the audit**; do not “fix” the
  tree silently.
- **Artifact hygiene:** Do **not** add generator or helper scripts under  
  `.cursor/audit-results/*/inventories/`. Keep reusable tooling in  
  `input/kaggle-ml-comp-scripts/scripts/layers/layer_2_devtools/` (see `README.md`).
- **Scoped outputs:** After each target, confirm new primary artifacts exist only
  under `.cursor/audit-results/<scope>/{inventories,audits,summaries}/` (see
  reference Step 1b).
- **Shell:** Do not instruct subagents to run Windows PowerShell 5.x one-liners
  using bash-style `&&` or `||` (invalid). Use separate commands or
  PowerShell-native flow (`if ($LASTEXITCODE -ne 0) { ... }`).
