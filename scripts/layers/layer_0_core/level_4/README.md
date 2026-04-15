# level_4

## Purpose

Orchestration layer for data loaders, feature extraction, ensembling, pipelines, file I/O, and runtime progress tracking. Composes level_0–3 into higher-level workflows.

## Contents

| Subpackage | Description |
|------------|-------------|
| dataloaders | Create train/val/test DataLoaders from DataFrames |
| ensemble | Stacking ensemble with meta-model validation |
| features | SigLIP embeddings and FeatureExtractor adapter |
| file_io | Load/save CSV, JSON, YAML, pickle, images, memmap |
| metrics | Task-aware metric dispatch (`calculate_metrics`, `calculate_metric_by_name`) and weighted R² factory |
| models | Vision model factory (DINOv2, timm) |
| pipeline | EvaluatePipeline, SubmissionAveragingWorkflow, threshold optimization |
| runtime | ProgressTracker for training and inference |

## Public API

| Export | Description |
|--------|-------------|
| create_dataloaders | Create train and validation DataLoaders |
| create_test_dataloader | Create test DataLoader |
| stacking_ensemble_with_validation | Stack base models with learned meta-model |
| compute_siglip_embeddings | Extract SigLIP embeddings from DataFrame |
| SigLIPFeatureExtractorAdapter | Adapter for SigLIP in FeatureExtractor interface |
| load_csv_raw, load_csv_raw_if_exists, load_csv, save_csv | CSV I/O |
| load_image_raw, load_image, save_image | Image I/O |
| load_json_raw, load_json, load_best_config_json, save_json, save_json_atomic | JSON I/O |
| should_use_memmap, create_memmap, load_memmap, save_memmap_with_metadata, load_memmap_with_metadata, MEMMAP_THRESHOLD_MB | Memmap utilities |
| load_pickle_raw, load_pickle, save_pickle | Pickle I/O |
| load_yaml_raw, load_yaml, save_yaml | YAML I/O |
| calculate_metrics, calculate_metric_by_name | Dispatch metrics by task type or registered name |
| create_weighted_r2_calculator | Create weighted R² calculator for regression |
| create_vision_model | Factory for vision models (DINOv2, timm) |
| EvaluatePipeline | Pipeline for evaluation |
| SubmissionAveragingWorkflow | Workflow for averaging submission files |
| optimize_threshold | Optimize threshold for multi-label classification |
| ProgressTracker | Progress bar and metrics tracking |

## Dependencies

- **level_0** — errors, paths, vision, runtime, prediction_guards, scoring
- **level_1** — BasePipeline, BaseVisionModel, `get_metric`, `list_metrics`, `validate_config_section_exists`, `validate_paired_predictions`, ProgressConfig, `get_device_info`
- **level_2** — dataloader, ensemble_strategies, models, validation, vision_transforms
- **level_3** — dataloader, ensemble, features, metrics, runtime, transforms

## Usage Example

```python
from layers.layer_0_core.level_4 import load_csv, create_dataloaders, create_vision_model, EvaluatePipeline

df = load_csv("data/train.csv", required_cols=["id", "target"])
train_loader, val_loader = create_dataloaders(
    train_df, val_df, image_dir="/path/to/images", target_cols=["target"]
)
model = create_vision_model("efficientnet_b0", num_classes=5)
pipeline = EvaluatePipeline(config, predictions=preds, ground_truth=y_true)
result = pipeline.execute()
```
