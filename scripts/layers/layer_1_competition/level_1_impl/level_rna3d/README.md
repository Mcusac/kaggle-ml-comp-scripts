# level_rna3d (Stanford RNA 3D Folding Part 2)

## Purpose

This package implements the `rna3d` contest for `KAGGLE_COMP_CONTEST=rna3d`: it registers with `ContestRegistry` on import and re-exports tiered APIs (`level_0`–`level_4`) as a single import surface.

## Contents

- **`__init__.py`** — Package docstring, triggers registration, aggregates subpackages `level_0`–`level_4`, and composes `__all__` from their exports.
- **`registration.py`** — Import-time `register_contest("rna3d", …)` wiring using config, schema, paths, and post-processor from `level_0` (not part of the public API).
- **`level_0/`** — Config, data schema, paths, post-processing, scoring, validation, artifacts, train labels, and notebook command builders.
- **`level_1/`** — Baseline approximation and related helpers.
- **`level_2/`** — Orchestration (trainer registry, tuning, submission).
- **`level_3/`** — Training pipeline entrypoints.
- **`level_4/`** — CLI / handler wiring for train, tune, and submit.

## Public API

Symbols are those listed in `level_rna3d/__init__.py` `__all__`: the union of `level_0.__all__` through `level_4.__all__`. Import from `layers.layer_1_competition.level_1_impl.level_rna3d` (or a specific `level_K` under it) per project import-surface rules. The `registration` module is intentionally not exported.

## Dependencies

- **`layers.layer_1_competition.level_0_infra.level_1.registry`** — `register_contest` to register this contest in `ContestRegistry`.
- **`layers.layer_1_competition.level_1_impl.level_rna3d.level_0`** — Types passed into `register_contest` (`RNA3DConfig`, `RNA3DDataSchema`, `RNA3DPaths`, `RNA3DPostProcessor`).

## Usage Example

```python
# Importing the package registers "rna3d" and exposes tier APIs.
from layers.layer_1_competition.level_1_impl import level_rna3d

# Example: use level_0 validation (also available on the root barrel if exported there).
from layers.layer_1_competition.level_1_impl.level_rna3d.level_0 import validate_rna3d_inputs
```
