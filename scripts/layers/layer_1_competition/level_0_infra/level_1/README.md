# infra/level_1 — Feature extraction, export, handlers

**On disk:** `scripts/layers/layer_1_competition/level_0_infra/level_1/`.  
**Import:** `layers.layer_1_competition.level_0_infra.level_1` (on-disk folder is `infra/level_1/`, not a `level_C1` junction).

## Purpose

Provides contest-agnostic feature extraction model creation, export pipeline orchestration, CLI command handlers, and validation. Sits above `layers.layer_1_competition.level_0_infra.level_0` and consumes its public API.

**General-stack coupling:** Some modules import general `level_N` above the minimum implied by infra tier (see `INFRA_GENERAL_LEVEL` in `audit_precheck` output under `.cursor/audit-results/competition_infra/summaries/`). That is treated as orchestration debt: prefer facades or moving heavy modules to `infra.level_2+` over silent violations.

## Contents

| Sub-package | Description |
|-------------|-------------|
| *(protocols)* | Defined under `infra/level_0/abstractions/`; exposed on `layers.layer_1_competition.level_0_infra.level_0` and re-exported from `layers.layer_1_competition.level_0_infra.level_1` where applicable |
| `handlers/` | CLI command handlers (train, test, grid_search, cross_validate, ensemble, export) |
| `export/` | Export model pipeline orchestration using `layers.layer_1_competition.level_0_infra.level_0` handlers |
| `features/` | Feature extraction model factory (SigLIP, DINOv2, timm) and input validation |

## Public API

All names exported from `__init__.py`:

- **Protocols:** ContestInputValidator, ContestMetric, ContestPipelineProtocol
- **Handlers:** get_command_handlers
- **Export:** export_model_pipeline
- **Features:** create_feature_extraction_model, set_pretrained_weights_resolver, validate_feature_extraction_inputs
- **Re-export:** TsvSubmissionFormatter (from level_1)

## Dependencies

- **level_0:** Command, get_arg, parse_comma_separated, ensure_dir, get_logger, get_torch
- **level_1:** TsvSubmissionFormatter, validate_feature_extraction_trainer_inputs
- **level_2:** simple_average
- **level_3:** SigLIPExtractor
- **level_4:** create_vision_model, SigLIPFeatureExtractorAdapter
- **level_5:** ExportPipeline
- **level_6:** PredictPipeline
- **level_8:** TrainPipeline
- **level_9:** CrossValidateWorkflow, HyperparameterGridSearch, TrainPredictWorkflow
- **layers.layer_1_competition.level_0_infra.level_0:** create_pipeline_kwargs, get_pretrained_weights_path, and handler entry points re-exported from the package root (e.g. handle_auto_detect, handle_best_variant_file, handle_just_trained_model, handle_results_file)

## Usage Example

```python
from layers.layer_1_competition.level_0_infra.level_1 import get_command_handlers, create_feature_extraction_model, export_model_pipeline

# Get CLI handlers for run.py (requires HandlerContextBuilder from run_helpers)
builder = get_handler_context_builder("csiro")
handlers = get_command_handlers(builder)

# Create feature extraction model
model = create_feature_extraction_model(
    model_name="siglip_so400m_patch14_384",
    num_primary_targets=10,
    device=torch.device("cuda"),
)

# Export model (requires ContestContext from infra level_0)
ctx = build_contest_context("csiro")
path = export_model_pipeline(ctx, model_dir="output/models/run_001")
```
