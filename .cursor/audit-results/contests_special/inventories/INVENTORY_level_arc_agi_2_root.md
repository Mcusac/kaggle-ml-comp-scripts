---
generated: 2026-04-08
audit_scope: contests_special
level_name: level_arc_agi_2_root
level_path: layers/layer_1_competition/level_1_impl/level_arc_agi_2
artifact_kind: inventory
---

# Inventory: `level_arc_agi_2` (implementation tree)

Contest implementation under `level_1_impl` (not under `contests/`). Import prefix: `layers.layer_1_competition.level_1_impl.level_arc_agi_2`.

## Package layout

| Tier | Role (typical) |
|------|----------------|
| `level_0` | Config, dataset, heuristics, ARC primitives, LM-TTA inference module, notebook commands |
| `level_1` | Models, scoring, eval, run tracking, Qwen formatting |
| `level_2` | Training, inference, LM backend, local eval pipeline |
| `level_3` | Trainer registry, neural eval, LLM-TTA runner |
| `level_4` | Submit strategy dispatch, stages |
| `level_5` | Orchestration stages |
| `level_6` | Contest pipeline, orchestration |
| `level_7` | CLI / notebook handlers |
| `registration.py` | `ContestRegistry` registration (mirrors other `level_1_impl` contests) |

## Entrypoints

- `__init__.py`: `registration` side effect; aggregates `level_0`–`level_7` public APIs.
- `registration.py`: `register_contest` and notebook/handler module strings.

## Machine precheck

`audit_precheck.py` may **fail or skip** when the devtools import chain hits optional deps (e.g. `torch`/`torchvision` in `layer_0_core` vision stack). Re-run from `scripts/` with a full framework venv for a complete Phase-7 report.

## Related tests

ARC behavior is covered under `layers/layer_2_devtools/level_1_impl/tests/unit/test_contest/test_arc_agi_2_*.py` (imports should use `level_0`–`level_6` barrels matching this inventory).
