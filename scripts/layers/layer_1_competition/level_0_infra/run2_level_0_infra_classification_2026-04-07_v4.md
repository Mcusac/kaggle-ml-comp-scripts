# Run 2 — `level_0_infra` classification (v4)

Generated: 2026-04-07

## Run 0 — Dependency Direction Audit (Recheck)

### Target

- `layers/layer_1_competition/level_0_infra`

### Method

- Scanned **all Python files** under the target (AST import parsing; `import ...` and `from ... import ...`).
- Validated for:
  - `# VIOLATION: dependency — imports higher level` (e.g., `level_0_infra` importing `layer_1_competition/level_1_impl`)
  - `# VIOLATION: dependency — circular` (cycles *within* `level_0_infra`)
  - `# VIOLATION: dependency — cross-layer leakage` (imports from non-allowed layer packages)

### Results

- **Files scanned**: 96
- **Parse errors**: 0
- **Violations found**: 0
- **Circular dependencies (internal)**: 0

### Notes (non-violations)

- A couple modules contain **string messages** referencing `layers.layer_1_competition.level_1_impl...` (e.g., “Import ...registration first.”). These are **not import statements** and were **not counted** as dependency violations.

## Run 1 — Classify Logic + Decomposition Candidates (Focused Fresh Pass)

Generated: 2026-04-07

### Target

- `layers/layer_1_competition/level_0_infra`

### Method (focused)

- Built an AST inventory of **all** `def`/`class` symbols (119 total) to spot:
  - core-heavy symbols (many `layer_0_core` imports/calls)
  - wrapper-shaped functions (single-return call)
  - multi-symbol “kitchen sink” modules
- Then did source reads on the highest-signal modules to confirm classification.

### Legend (required categories)

- **(1)** Competition-specific infra (VALID)
- **(2)** Generic utility (should move to `layer_0_core`)
- **(3)** Thin wrapper around `layer_0_core`
- **(4)** Duplicate logic from core
- **(5)** Overly high-level orchestration
- **(6)** Mixed-responsibility module

---

### High-signal findings (focused)

#### `level_0/cli_handlers_dispatch.py`

**Symbols**

- `list_contests_with_cli_handlers` — **(1)** competition dispatch surface (registry over contest “registration” side effects).
- `get_cli_handlers_module` — **(1)** contest implementation is intentionally *not* imported; runtime import by registered module path.
- `register_cli_handlers_module` — **(1)** registration hook.

**Notes**

- No direct contest-impl imports here (good); string message references `level_1_impl` are *not* dependency edges.

#### `level_1/handlers/command_handlers.py`

**Symbols**

- `_make_handlers` — **(1)** CLI routing table assembly.
- `get_command_handlers` — **(3)** thin wrapper over `_make_handlers`.
  - # VIOLATION: wrapper — no added value

**Decomposition**

- # CANDIDATE: decompose — orchestration should remain thin  
  Keep the “public surface” function, but avoid double-indirection wrappers unless they carry validation/compat logic.

#### `level_1/paths/env_paths.py`

**Module classification:** **(6)** mixed responsibility (environment path utilities + contest registry selection).

**Symbols**

- `get_run_py_path` — **(2)** generic repo-layout helper (path derivation) more “core/dev tooling” than competition infra.
  - # CANDIDATE: move to layer_0_core
- `get_data_root_path` — **(1)** competition-specific contest selection via `ContestRegistry` + `KAGGLE_COMP_CONTEST`.
- `get_output_path` / `get_input_path` — **(3)** wrappers over core `get_environment_root` / `resolve_environment_path`.
  - # VIOLATION: wrapper — no added value
  - # CANDIDATE: move to layer_0_core (if not already present as an equivalent API)
- `get_model_path` — **(2)** generic path convention helper (models/<name>[_ver].pkl).
  - # CANDIDATE: move to layer_0_core
- `get_best_model_path` / `get_submission_path` / `get_checkpoint_path` / `get_log_path` — **(3)** opinionated subpath wrappers.
  - # VIOLATION: wrapper — no added value

**Decomposition**

- # CANDIDATE: decompose — split into focused modules
  - `env_paths_core.py`: pure environment root/path helpers (core-eligible)
  - `contest_selection.py`: `ContestRegistry` + env var contest selection (infra-eligible)
- # CANDIDATE: decompose — extract helper to lower level  
  Extract “select contest name from env/registry” as a single function (reduces duplication risk across other entrypoints).

#### `level_1/contest/csv_io.py`

**Symbols**

- `read_csv_if_exists` — **(2)** generic IO utility (existence check + load).
  - # CANDIDATE: move to layer_0_core
- `load_training_csv` — **(1)** competition infra: conditional contest-specific loader fallback to core `load_csv_raw`.
- `load_test_csv` — **(3)** thin wrapper over `read_csv_if_exists` (logging only).
  - # VIOLATION: wrapper — no added value

**DRY / duplication**

- No confirmed core duplication (uses core loader), but `read_csv_if_exists` is a common utility shape:
  - # CANDIDATE: move to layer_0_core

#### `level_1/contest/splits.py`

**Symbols**

- `split_train_val` — **(3)** orchestrates `create_kfold_splits`/`get_fold_data` (core) and falls back to sklearn `train_test_split`.
  - # VIOLATION: wrapper — no added value
  - # CANDIDATE: move to layer_0_core (generic split policy helper)

**Decomposition**

- # CANDIDATE: decompose — extract helper to lower level  
  Split into two helpers: `kfold_split(...)` and `holdout_split(...)` (both core-eligible), leaving infra to choose policy.

#### `level_5/submission/io.py`

**Symbols**

- `save_submission` — **(2)** generic submission persistence policy (env output path + Kaggle mirror write).
  - # CANDIDATE: move to layer_0_core

**Rationale**

- “Kaggle runtime path mirroring” looks like environment/runtime policy, not competition-specific logic.

#### `level_5/submission/formatting.py`

**Symbols**

- `expand_predictions_to_submission_format` — **(1)** competition infra: transforms predictions to contest-defined submission rows via `contest_config`, `data_schema`, `post_processor`.

**Notes**

- Uses core `load_and_validate_test_data`, but adds real competition-domain assembly (not a wrapper).

#### `level_4/fold_orchestration/single_fold.py`

**Symbols**

- `train_single_fold` — **(5)** high-level orchestration (device selection + dataloaders + trainer + train loop + cleanup).
  - # CANDIDATE: move to higher level
  - # CANDIDATE: decompose — orchestration should remain thin

**Decomposition**

- Suggested boundaries:
  - `build_fold_dataloaders(...)` (lower-level helper; could be core-eligible if generalized)
  - `run_fold_training(...)` (workflow-level orchestration; higher-level)
  - keep infra layer thin: glue only, no policy branching beyond config wiring

#### `level_3/trainer/feature_extraction.py`

**Symbols**

- `FeatureExtractionTrainer` — **(5)** substantial training implementation + policy (two-stage extraction + regression fit + metric contract + save policy).
  - # CANDIDATE: move to higher level
  - # CANDIDATE: decompose — split into focused modules
  - # CANDIDATE: decompose — orchestration should remain thin

**Why not “core”?**

- The class relies on a **contest-provided** metric callable and contest config keys; it’s closer to “workflow implementation” than generic infra primitives.

**Decomposition proposal**

- Extract lower-level helpers (core-eligible if made contest-agnostic):
  - feature extraction loop (loader → features/targets)
  - fold feature split utilities (already core has `split_features_by_fold`)
  - regression train/eval wrapper
  - model saving policy (already core has `save_regression_model`)
- Keep a thin “trainer façade” in infra only if it provides stable interfaces used by multiple contests; otherwise locate the concrete trainer in `level_1_impl`.

---

### Items explicitly *not* flagged in this focused pass

- # VIOLATION: DRY — duplicates layer_0_core  
  Not confirmed from the sampled modules. Several functions are *wrappers* around core (flagged as wrapper/no-added-value) rather than logic duplicates.

## Run 2 — Duplication Detection (Missed Logic)

Generated: 2026-04-07

### Scope (strict)

- Read the v4 reference first (this file).
- Compared **only** the Run 1 items flagged as **generic / wrapper / move-to-core** against `layer_0_core`.

### Results

#### Confirmed duplicated snippets / helpers

- `level_5/submission/io.py:save_submission`
  - Duplicates core logic for computing the canonical “submission.csv location” string:
    - core uses: `"/kaggle/working/submission.csv" if is_kaggle() else resolve_environment_path("submission.csv", purpose="output")`
      - located in `layer_0_core/level_3/ensemble_strategies/pipeline_result_handler.py`
    - infra re-implements the same environment-conditional path and then adds a “mirror write” policy.
  - # VIOLATION: DRY — duplicated from layer_0_core

#### Not duplicates (core provides primitives; infra composes or wraps)

- `level_1/paths/env_paths.py:get_output_path` / `get_input_path`
  - Core already provides `get_environment_root(...)` and `resolve_environment_path(...)`; infra functions are wrappers/convenience, not independent reimplementations.
- `level_1/contest/splits.py:split_train_val`
  - Uses core CV split primitives (`create_kfold_splits`, `get_fold_data`) and an external fallback (`sklearn.model_selection.train_test_split`); no matching single core helper was found with the same combined policy.
- `level_1/contest/csv_io.py:read_csv_if_exists`
  - No direct `layer_0_core` equivalent with the same “exists→load_csv_raw else None” helper name/shape was found in this pass.

## Run 3 — Thin Wrapper Detection (Second Pass)

Generated: 2026-04-07

### Scope (strict)

- Read the v4 reference first (this file).
- Reviewed **only** symbols previously flagged as possible wrappers in Run 1:
  - `level_1/handlers/command_handlers.py:get_command_handlers`
  - `level_1/contest/csv_io.py:load_test_csv`
  - `level_1/contest/splits.py:split_train_val`
  - `level_1/paths/env_paths.py:get_output_path`, `get_input_path`,
    `get_best_model_path`, `get_submission_path`, `get_checkpoint_path`, `get_log_path`

### Wrapper findings (confirmed)

- `level_1/handlers/command_handlers.py:get_command_handlers`
  - Pure delegation to `_make_handlers(builder)` with unchanged args/return.
  - # VIOLATION: wrapper — no added value

- `level_1/contest/csv_io.py:load_test_csv`
  - Delegates to `read_csv_if_exists(test_csv_path)` and only adds a debug log on `None`.
  - # VIOLATION: wrapper — no added value

- `level_1/paths/env_paths.py:get_best_model_path`
  - One-line delegation: `return get_output_path("best_model")`
  - # VIOLATION: wrapper — no added value

- `level_1/paths/env_paths.py:get_submission_path`
  - One-line delegation: `return get_output_path(filename)`
  - # VIOLATION: wrapper — no added value

- `level_1/paths/env_paths.py:get_checkpoint_path`
  - One-line delegation: `return get_output_path(f"checkpoints/{experiment_name}/epoch_{epoch}.pkl")`
  - # VIOLATION: wrapper — no added value

- `level_1/paths/env_paths.py:get_log_path`
  - One-line delegation: `return get_output_path(f"logs/{log_name}")`
  - # VIOLATION: wrapper — no added value

### Wrapper findings (borderline / policy wrappers)

- `level_1/paths/env_paths.py:get_output_path` and `get_input_path`
  - Mostly wrapper behavior around core `resolve_environment_path(...)` / `get_environment_root(...)`,
    but they encode a tiny policy: empty string → root, else resolve `<relative_path>`.
  - # VIOLATION: wrapper — no added value

- `level_1/contest/splits.py:split_train_val`
  - Not a one-line delegation; it composes core CV helpers and falls back to sklearn holdout split.
  - Kept flagged as wrapper/no-added-value from Run 1, but it’s “thin orchestration” rather than a pure delegation.
  - # VIOLATION: wrapper — no added value

## Run 4 — Decomposition Pass (Refined)

Generated: 2026-04-07

### Scope (strict)

- Read the v4 reference first (this file).
- Analyzed **only** modules previously flagged as **(6) mixed-responsibility**.

### Decomposition plan (mixed-responsibility modules)

#### `level_1/paths/env_paths.py` (mixed: env-path utilities + contest registry selection)

# CANDIDATE: decompose — split into focused modules

- **Split by responsibility**:
  - **Environment path convenience** (core-eligible):
    - `get_output_path`
    - `get_input_path`
    - `get_model_path`
    - `get_best_model_path`
    - `get_submission_path`
    - `get_checkpoint_path`
    - `get_log_path`
    - (optionally) `get_run_py_path` if it’s treated as repo/dev tooling rather than contest infra
  - **Contest selection / registry coupling** (infra-eligible):
    - `get_data_root_path` (depends on `ContestRegistry`, `get_contest`, `KAGGLE_COMP_CONTEST`)

# CANDIDATE: decompose — extract helper to lower level

- Extract a single, reusable helper for “pick contest name” policy to avoid re-implementations elsewhere:
  - `select_contest_name(*, available: list[str], env_var: str = "KAGGLE_COMP_CONTEST") -> str`
  - This helper can live in the contest-selection module (infra) or in core **only** if you intend core to own env-var selection policy.

# CANDIDATE: decompose — orchestration should remain thin

- Keep `get_data_root_path` as a thin orchestrator that:
  - fetches `available = ContestRegistry.list_contests()`
  - selects contest name via the extracted `select_contest_name(...)`
  - resolves `contest = get_contest(name)` and returns `contest["paths"]().local_data_root`

**Suggested module boundaries (names illustrative)**

- `level_1/paths/environment_paths.py` (or core target if moved): environment-root + relative-path convenience wrappers.
- `level_1/registry/contest_selection.py`: contest name selection + `get_data_root_path` (or just the selection helper), isolated from generic path helpers.

## Run 5 — Layer Size Normalization + Responsibility Enforcement

Generated: 2026-04-07

### Scope (strict)

- Read the v4 reference first (this file).
- **Did not rescan modules**; this summary is based only on previously flagged / previously read modules from Runs 1–4.

### Findings (size + responsibility)

#### Thick infra (orchestration mixed with implementation)

- `level_3/trainer/feature_extraction.py:FeatureExtractionTrainer`
  - Owns substantial workflow implementation (feature extraction + regression fit + metric contract + save policy wiring).
  - # VIOLATION: infra-too-thick

- `level_4/fold_orchestration/single_fold.py:train_single_fold`
  - High-level orchestration (device selection + dataloaders + trainer lifecycle + cleanup).
  - # VIOLATION: infra-too-thick

#### Excessive wrappers (surface inflation)

- `level_1/paths/env_paths.py`
  - Multiple one-line delegations (`get_best_model_path`, `get_submission_path`, `get_checkpoint_path`, `get_log_path`) and near-wrapper helpers (`get_output_path`, `get_input_path`).
  - This inflates infra surface area without adding durable policy (beyond subpath strings).
  - # VIOLATION: infra-too-thick
  - # CANDIDATE: push-down-to-core (environment-root/path convenience)

- `level_1/handlers/command_handlers.py:get_command_handlers`
  - Pure delegation to `_make_handlers(builder)`.
  - # VIOLATION: infra-too-thick

- `level_1/contest/csv_io.py:load_test_csv`
  - Thin wrapper around `read_csv_if_exists` (only adds debug log).
  - # VIOLATION: infra-too-thick

#### Registry duplication / parallel registries

- `level_0/cli_handlers_dispatch.py` maintains an internal registration map (`_CLI_HANDLERS_MODULES`) and runtime import dispatch that is separate from `ContestRegistry`-based selection used elsewhere (e.g., `env_paths.py:get_data_root_path`).
  - This is a second registry-like system inside infra (one for contests, one for CLI handlers), increasing coordination burden.
  - # VIOLATION: registry-duplication

#### Inline IO (IO policy embedded in infra)

- `level_5/submission/io.py:save_submission`
  - Performs direct file output selection and writes CSV (including Kaggle mirror write policy).
  - # VIOLATION: inline-io
  - # CANDIDATE: push-down-to-core (if core is meant to own environment + Kaggle IO policy)

- `level_1/contest/csv_io.py:read_csv_if_exists` / `load_training_csv` / `load_test_csv`
  - Owns CSV existence-check IO policy and contest-loader fallback policy.
  - `read_csv_if_exists` is reusable; `load_training_csv` is contest-facing policy glue.
  - # VIOLATION: inline-io
  - # CANDIDATE: push-down-to-core (`read_csv_if_exists` only)

### Responsibility enforcement summary

- If infra is meant to stay thin, the main normalization lever is to **push down reusable helpers** (env-path convenience, “csv-if-exists”, submission path derivation) into `layer_0_core`, and **push up workflow implementations** (`FeatureExtractionTrainer`, fold orchestration) into higher layers.

## Run 6 — Cleanup + Refactor (Incremental)

Generated: 2026-04-07

### Completed (incremental)

- `level_1/handlers/command_handlers.py:get_command_handlers`
  - # VIOLATION: wrapper — no added value ✅ removed extra indirection (deleted `_make_handlers`, kept API)

- `level_1/contest/csv_io.py:load_test_csv`
  - # VIOLATION: wrapper — no added value ✅ removed (call site updated)

- “submission.csv location” snippet duplication
  - # VIOLATION: DRY ✅ consolidated via core helper
  - Added `layer_0_core/level_1/runtime/paths.py:get_default_submission_csv_path(...)`
  - Updated:
    - `layer_0_core/level_3/ensemble_strategies/pipeline_result_handler.py`
    - `level_0_infra/level_5/submission/io.py:save_submission`

## Run 7 — Post Cleanup Validation (Second Pass)

Generated: 2026-04-07

### Validation scope

- Validate only (no code edits).
- Checks performed:
  - remaining thin wrappers (previously flagged)
  - remaining duplication (previously confirmed snippet)
  - remaining inline IO in infra
  - registry centralization
  - dependency direction regressions (imports to higher layers / outside allowed surfaces)

### Results

#### Wrappers

- `level_1/contest/csv_io.py:load_test_csv` no longer exists (removed in Run 6) ✅
- Remaining wrapper functions still present in `level_1/paths/env_paths.py`:
  - `get_best_model_path`, `get_submission_path`, `get_checkpoint_path`, `get_log_path`
  - also near-wrapper `get_output_path`, `get_input_path`
  - # REGRESSION: wrapper

#### Duplication

- The previously confirmed duplicated “submission.csv location” snippet is now consolidated via
  `layer_0_core.level_1.runtime.paths:get_default_submission_csv_path(...)` (used by both infra + core) ✅
- No new duplication regressions were detected in this focused validation.

#### Inline IO

- Inline IO remains in infra:
  - `level_5/submission/io.py:save_submission` writes CSV
  - `level_1/contest/data_loading.py` still does `pd.read_csv(...)` for tabular path
  - # REGRESSION: inline-io

#### Registry centralization

- Registry duplication remains:
  - `level_0/cli_handlers_dispatch.py` uses `_CLI_HANDLERS_MODULES` dispatch map separate from `ContestRegistry`
  - # REGRESSION: registry-duplication

#### Dependency direction

- AST import validation over `level_0_infra` found **0** imports from `layer_1_competition/level_1_impl` and **0** cross-layer leakage regressions.
  - (no flags)

## Run 7b — Post Cleanup Validation (After Run 8 plan execution)

Generated: 2026-04-07

### Wrapper regression check

- Remaining `env_paths.py` wrappers (`get_output_path`, `get_input_path`, `get_best_model_path`, `get_submission_path`, `get_checkpoint_path`, `get_log_path`) are now **removed** (definitions no longer present in `level_0_infra`).
  - (no `# REGRESSION: wrapper`)

### Duplication regression check

- “submission.csv location” duplication remains **consolidated** in core and infra no longer maintains its own copy.\n
### Inline-IO regression check

- No `pd.read_csv(...)`, `to_csv(...)`, or `save_csv(...)` calls remain inside `level_0_infra`.\n
### Registry centralization check

- `_CLI_HANDLERS_MODULES` dispatch map is removed; CLI handler module registration is now stored on `ContestRegistry` entries via `level_1/registry/cli_handlers.py`.\n
### Dependency direction check

- AST import validation over `level_0_infra` still reports **0** higher-layer imports and **0** cross-layer leakage.


