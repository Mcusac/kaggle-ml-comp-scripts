# `level_0_infra`

Shared devtools infrastructure with a strict dependency ordering.

## Tiers

```text
level_0   — Atomic modules (constants, path, io, parse, scan/health_analyzers, format, contracts, …).
level_1   — Compositions that depend only on level_0 (e.g. `SectionFormatters`, rollup skeleton markdown,
            hyperparameter *analysis*, threshold checker over analysis dicts).
level_2   — `ConsoleReporter`: human-readable reports using `level_0` reporter base + `level_1` section formatters.
```

Rules:

- **`level_0`** must not import **`level_1`** or **`level_2`**.
- **`level_1`** may import **`level_0`** only.
- **`level_2`** may import **`level_0`** and **`level_1`**.

## Public surfaces

- **`level_0_infra` package root** re-exports **`level_0`** only, including star-exported subpackages such as `constants`, `format`, `path`, `scan`, `hyperparameter` (utils), etc. Import **`level_1`** / **`level_2`** explicitly when you need composed helpers or the console reporter.
- **`level_1`** exposes `SectionFormatters`, rollup builder, checker types, and hyperparameter analysis functions via its `__init__.py`.

## Hyperparameter split

- **`level_0.hyperparameter`**: `hyperparameter_utils` only (metadata I/O, combinations, model parameter names).
- **`level_1.hyperparameter_analysis`**: statistics and recommendations (may use `layer_0_core` when available).
