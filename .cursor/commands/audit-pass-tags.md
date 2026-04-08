# audit-pass-tags

Shared **flag taxonomy** for multi-pass audits. Use these exact prefixes so findings are greppable and comparable across runs.

Reference this file from every `/audit-pass-*` invocation when recording human-readable summaries.

## Dependency and layering

- `# VIOLATION: dependency — imports higher level`
- `# VIOLATION: dependency — circular`
- `# VIOLATION: dependency — cross-layer leakage`
- `# VIOLATION: dependency — contest impl / wrong surface`

## DRY and reuse

- `# VIOLATION: DRY — duplicates layer_0_core`
- `# VIOLATION: DRY — duplicated from layer_0_core`
- `# VIOLATION: DRY — near-duplicate`

## Wrappers and surfaces

- `# VIOLATION: wrapper — no added value`  
  Do **not** use this for `__init__.py` aggregation that follows `python-import-surfaces.mdc`.
- `# NOTE: barrel — intentional re-export`  
  Use when `__init__.py` aggregation is valid by policy.

## Placement and structure

- `# CANDIDATE: move to layer_0_core`
- `# CANDIDATE: move to higher level`
- `# CANDIDATE: push-down-to-core`
- `# CANDIDATE: decompose — split into focused modules`
- `# CANDIDATE: decompose — extract helper to lower level`
- `# CANDIDATE: decompose — orchestration should remain thin`

## Infra-specific heuristics (use when auditing competition infra)

- `# VIOLATION: infra-too-thick`
- `# VIOLATION: inline-io`
- `# VIOLATION: registry-duplication`

## Post-fix validation

- `# REGRESSION: wrapper`
- `# REGRESSION: duplication`
- `# REGRESSION: inline-io`
- `# REGRESSION: dependency`

## Classification legend (optional table in classify pass)

| # | Meaning |
|---|--------|
| **(1)** | Competition-specific infrastructure — valid in infra / contest layer |
| **(2)** | Generic utility — consider `layer_0_core` |
| **(3)** | Thin wrapper around `layer_0_core` |
| **(4)** | Duplicate of or near-duplicate of `layer_0_core` |
| **(5)** | Overly high-level orchestration — consider higher layer |
| **(6)** | Mixed responsibility — decompose |

This command supports discoverability for `/audit-pass-*` workflows. It may appear as a secondary doc in the command picker when using repo-local commands.
