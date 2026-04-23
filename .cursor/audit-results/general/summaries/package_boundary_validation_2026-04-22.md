---
generated: 2026-04-22
artifact: package_boundary_validation
---

# Package Boundary Validation Report

- Scripts root: `C:/Users/mdc0431/OneDrive - UNT System/Documents/Kaggle/code/input/kaggle-ml-comp-scripts/scripts`
- Scope root: `C:/Users/mdc0431/OneDrive - UNT System/Documents/Kaggle/code/input/kaggle-ml-comp-scripts/scripts/layers/layer_2_devtools`
- Files scanned: 224
- Violations: 1 (upward=1 illegal_external=0)

## Nodes

- `devtools_impl_level_0`: devtools impl level_0
- `devtools_impl_level_1`: devtools impl level_1
- `devtools_impl_level_2`: devtools impl level_2
- `devtools_infra_level_0`: devtools infra level_0
- `devtools_infra_level_1`: devtools infra level_1
- `devtools_infra_level_2`: devtools infra level_2
- `general_level_0`: general level_0
- `general_level_4`: general level_4
- `general_level_5`: general level_5

## Boundary matrix (counts; only observed internal edges)

| source\target | `devtools_impl_level_0` | `devtools_impl_level_1` | `devtools_impl_level_2` | `devtools_infra_level_0` | `devtools_infra_level_1` | `devtools_infra_level_2` | `general_level_0` | `general_level_4` | `general_level_5` |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `devtools_impl_level_0` | 38 |  |  | 43 | 4 | 1 |  | 1 |  |
| `devtools_impl_level_1` | 16 | 6 | 1 | 55 | 9 | 1 |  |  |  |
| `devtools_impl_level_2` | 2 | 37 | 6 | 25 | 1 |  |  |  |  |
| `devtools_infra_level_0` |  |  |  | 93 |  |  | 1 | 1 | 2 |
| `devtools_infra_level_1` |  |  |  | 43 | 14 |  |  |  | 1 |
| `devtools_infra_level_2` |  |  |  | 2 | 2 |  |  |  |  |
| `general_level_0` |  |  |  |  |  |  |  |  |  |
| `general_level_4` |  |  |  |  |  |  |  |  |  |
| `general_level_5` |  |  |  |  |  |  |  |  |  |

## Violating pairs (examples)

- `devtools_impl_level_1` -> `devtools_impl_level_2`
  - `scripts/layers/layer_2_devtools/level_1_impl/level_1/api_pipeline.py`: `from layers.layer_2_devtools.level_1_impl.level_2.pipeline_ops import ...` -> `layers.layer_2_devtools.level_1_impl.level_2.pipeline_ops`

