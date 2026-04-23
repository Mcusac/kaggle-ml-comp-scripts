# health-check

Comprehensive code health analysis for the kaggle-ml-comp-scripts package.

**Working directory** for all `python -m ...` invocations: `input/kaggle-ml-comp-scripts/scripts/`. See [layer_2 devtools README](../../input/kaggle-ml-comp-scripts/scripts/layers/layer_2_devtools/README.md).

## Primary Health Check

Run the main health check analysis (from the repo root, two steps: `cd` then run):

```bash
cd "input/kaggle-ml-comp-scripts/scripts"
python -m layers.layer_2_devtools.level_1_impl.level_2.check_health --root ".."
```

**With JSON output (for further analysis):**

```bash
cd "input/kaggle-ml-comp-scripts/scripts"
python -m layers.layer_2_devtools.level_1_impl.level_2.check_health --root ".." --json > ../health_report.json
```

**With custom threshold config:**

```bash
cd "input/kaggle-ml-comp-scripts/scripts"
python -m layers.layer_2_devtools.level_1_impl.level_2.check_health --root ".." --config ../thresholds.json
```

**What it analyzes:**

- **File metrics:** line counts, long functions, large classes
- **Complexity:** cyclomatic complexity for functions and classes
- **Imports:** dependency graph, deep imports, orphaned modules
- **Import path validation:** incorrect relative import paths
- **Type annotations:** missing type annotation imports
- **Cohesion:** internal vs external import ratio
- **Duplication:** code clone detection (with false positive filtering)
- **SOLID:** principle violation detection
- **Dead code:** unused imports, unreachable code

**Options:**

- `--root PATH`: Root directory to analyze (default: current directory)
- `--json`: Output JSON format instead of console report
- `--config FILE`: Use custom threshold configuration file
- `--no-complexity`: Skip complexity analysis
- `--no-duplication`: Skip duplication detection
- `--no-solid`: Skip SOLID checks
- `--no-dead-code`: Skip dead code detection

## CI parity (machine runner and GitHub Actions)

[`.github/workflows/health-check.yml`](../../input/kaggle-ml-comp-scripts/.github/workflows/health-check.yml) runs, in order:

1. **Machine pipeline** — `run_code_audit_pipeline` with `--workspace-root ..`, a unique `--run-id`, `--strict` (strict precheck), and `--fail-on-skipped` (any manifest step with `status: "skipped"`, e.g. disabled segment or missing CSIRO tree, fails the step). This matches **`Task(code-audit-runner)`** / the unified audit machine entry, not a one-off `scan_*.py` (CSIRO is included in the pipeline when `run_csiro_scan` is on).
2. **Health JSON** — `check_health --root .. --json` → `health_report.json` at the package root.
3. **Thresholds** — `check_health_thresholds` with `--strict` (warnings fail the run).

**Match CI locally** (from `kaggle-ml-comp-scripts/scripts/`; pick any unused `ci-local-<label>` for `--run-id`):

```bash
cd "input/kaggle-ml-comp-scripts/scripts"
python -m layers.layer_2_devtools.level_1_impl.level_2.run_code_audit_pipeline \
  --workspace-root ".." \
  --run-id "ci-local-manual" \
  --strict \
  --fail-on-skipped
python -m layers.layer_2_devtools.level_1_impl.level_2.check_health --root ".." --json > ../health_report.json
python -m layers.layer_2_devtools.level_1_impl.level_2.check_health_thresholds ../health_report.json --strict
```

**Artifacts in CI:** the workflow uploads `health_report.json` (and a pretty copy when present) and the machine run directory `code-audit-manifest` (under `.cursor/audit-results/general/summaries/machine_runs/<run_id>/`, containing `manifest.json` and `audit_queue.json`).

## Additional Health Tools

### Threshold Validation

Validate code against quality thresholds (useful for CI/pre-commit):

```bash
cd "input/kaggle-ml-comp-scripts/scripts"
python -m layers.layer_2_devtools.level_1_impl.level_2.check_health --root ".." --json > ../health_report.json
python -m layers.layer_2_devtools.level_1_impl.level_2.check_health_thresholds ../health_report.json --config ../thresholds.json --strict
```

**Exit codes:**

- `0`: All checks passed
- `1`: Fatal violations found
- `2`: Warnings only (strict mode)

### Import Cleanup

Remove unused imports based on health report:

```bash
cd "input/kaggle-ml-comp-scripts/scripts"
python -m layers.layer_2_devtools.level_1_impl.level_2.cleanup_imports --report ../health_report.json --dry-run
python -m layers.layer_2_devtools.level_1_impl.level_2.cleanup_imports --report ../health_report.json
```

### Pre-Upload Validation

**Always run before uploading to Kaggle.** From `kaggle-ml-comp-scripts/scripts/`:

```bash
cd "input/kaggle-ml-comp-scripts/scripts"
python -m layers.layer_2_devtools.level_1_impl.level_2.validate_before_upload
python -m layers.layer_2_devtools.level_1_impl.level_2.validate_before_upload --verbose
```

**What it checks:**

- All contest implementation modules can be imported
- No missing type annotation imports (`Dict`, `Tuple`, etc.)
- No structural import errors
- Syntax errors

**Exit codes:**

- `0`: All checks passed - safe to upload
- `1`: Structural errors found - must fix before upload

### Import Verification

```bash
cd "input/kaggle-ml-comp-scripts/scripts"
python -m layers.layer_2_devtools.level_1_impl.level_2.verify_imports
```

## Health analysis implementation

The analyzers, thresholds, and `api_*` facades live under [layer_2_devtools](../../input/kaggle-ml-comp-scripts/scripts/layers/layer_2_devtools) (not under `scripts/dev/health/…` — that path is obsolete).

## Recommended Workflow

1. **Before major changes:** Run full health check (see **Primary Health Check** above).
2. **Before uploading to Kaggle:** `validate_before_upload` (see **Pre-Upload Validation**).
3. **After refactoring:** JSON report, `check_health_thresholds`, and optional `cleanup_imports` (see **Threshold validation** and **Import cleanup**).

## Code Duplication Detection

The duplication detector uses a 6-line sliding window with MD5 hashing to identify duplicate code blocks.

### Filtering Behavior

**False positives are automatically filtered:**

- **Import-only blocks:** All lines are imports (e.g., `import logging`, `from pathlib import Path`)
- **Boilerplate blocks:** Common patterns like `logger = logging.getLogger(__name__)`
- **Overlapping windows:** Same-file duplicates that are likely detector artifacts (adjacent windows)

**Expected results after filtering:**

- **Total duplicates:** <200 (down from ~450 without filtering)
- **Actionable duplicates:** <30 (blocks appearing in 3+ files, >10 lines)

### Interpreting Duplication Reports

**Acceptable patterns** (no action needed):

- **Docstring similarity:** Similar functions should have similar docstrings
- **Config vs Implementation:** Config data vs implementation code (good separation of concerns)
- **Similar but distinct:** Similar structure, different purposes (good modularity)
- **Common imports/boilerplate:** Standard Python patterns

**Actionable opportunities** (consider refactoring):

- **High frequency:** Blocks appearing in 3+ files
- **Large blocks:** Duplicates >10 lines
- **Identical logic:** Same purpose/context (not just similar structure)

**Criteria for refactoring** (ALL must be true):

1. Identical logic (not just similar structure)
2. Appears in 3+ files (not just 2)
3. >10 lines (not just 6-line window artifacts)
4. Same purpose/context (not different use cases)
5. Extraction improves maintainability (not over-abstraction)

### Detailed Duplicate Analysis

For detailed analysis of duplicates, use the analysis script:

```bash
python analyze_duplicates_detailed.py health_report.json input/kaggle-ml-comp-scripts
```

This script categorizes duplicates and identifies actionable refactoring opportunities.

### Principles

- **Preserve Good Code**: Don't refactor good patterns just because they're similar
- **YAGNI**: Don't create abstractions unless there's actual duplication
- **KISS**: Similar patterns in different contexts are OK
- **DRY**: Only apply when there's actual repetition, not just similarity
- **SOLID**: Maintain good separation of concerns

This command will be available in chat with /health-check
