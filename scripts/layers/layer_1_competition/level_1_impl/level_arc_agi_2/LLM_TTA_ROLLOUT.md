# ARC LLM-TTA Rollout Guide

## Modes
- `surrogate`: Uses package-native augmentation + constrained decoding without external LLM backend.
- `lm_backend`: Requires `--llm-model-path`; enables backend loading and task adaptation loop.

## Backward Compatibility
- Notebook command shape remains unchanged.
- Existing `single`, `ensemble`, and CNN paths remain valid.
- `llm_tta_dfs` now supports explicit mode selection (`--llm-execution-mode`).

## Recommended Rollout
1. Start with `surrogate` mode to verify pipeline integration and telemetry.
2. Run `lm_backend` with `mock://arc` to validate non-crashing LM plumbing.
3. Switch to real model path in controlled benchmark runs.
4. Tune runtime profile flags for target Kaggle hardware.
5. Promote LM mode to default only after benchmark stability.

## Guardrails
- Surrogate mode rejects LM-only flags to avoid silent no-op behavior.
- Runtime budgets (`max/task/decode`) are surfaced in metadata and stop reasons.
- Stacking/ensemble-weight flags are explicitly rejected for ARC submit path when inapplicable.

## Benchmark Entry Point
- `layers/layer_2_devtools/level_1_impl/benchmarks/arc_llm_tta_benchmark.py`
