# level_6

## Purpose

Level 6 provides ensembling methods, prediction pipelines, grid search infrastructure, tabular and vision model training, and variant management for ML competition workflows.

## Contents

| Package | Description |
|---------|-------------|
| `ensembling/` | EnsemblingMethod implementations (simple, weighted, ranked, percentile, target-specific) |
| `grid_search/` | Grid search base, result handlers, variant grid, focused parameter grid, cleanup |
| `metadata/` | Combo and metadata lookup helpers |
| `prediction/` | PredictPipeline and `create_streaming_test_dataloader` (CSV + streaming dataset; distinct from layers.layer_0_core.level_4 DataFrame factory) |
| `tabular/` | TabularTrainer, TabularPredictor, MLPModel |
| `tabular_models/` | Linear and tree tabular model wrappers (LogisticRegression, Ridge, XGBoost, LightGBM) |
| `vision/` | JSON-backed vision model registry (`get_vision_model_config`, `list_vision_models`) |

## Public API

| Name | Description |
|------|-------------|
| `SimpleAverageEnsemble` | Equal-weight ensemble |
| `WeightedAverageEnsemble` | Score-proportional ensemble |
| `RankedAverageEnsemble` | Model-rank-weighted ensemble |
| `PercentileAverageEnsemble` | Percentile-weighted ensemble |
| `TargetSpecificEnsemble` | Per-target model selection |
| `MLPModel` | Multi-layer perceptron for tabular data |
| `create_variant_specific_data` | Create variant-specific data dict |
| `create_variant_key` | Create variant key for deduplication |
| `create_variant_key_from_result` | Create variant key from result dict |
| `create_regression_variant_key_from_result` | Create regression variant key |
| `get_default_hyperparameters` | Default transformer hyperparameters |
| `GridSearchBase` | Abstract base for grid search pipelines |
| `handle_hyperparameter_grid_search_result` | Handle hyperparameter grid search CLI result |
| `handle_dataset_grid_search_result` | Handle dataset grid search CLI result |
| `handle_regression_grid_search_result` | Handle regression grid search CLI result |
| `LogisticRegressionModel` | Logistic regression classifier |
| `RidgeModel` | Ridge classifier |
| `XGBoostModel` | XGBoost classifier |
| `LightGBMModel` | LightGBM classifier |
| `TabularTrainer` | Trainer for tabular models |
| `TabularPredictor` | Predictor for tabular models |
| `PredictPipeline` | Prediction pipeline for vision/tabular |
| `create_streaming_test_dataloader` | Test DataLoader from CSV path using streaming dataset |
| `get_focused_parameter_grid` | Focused grid from previous results |
| `find_combo_id_from_config` | Resolve combo id from config using metadata |
| `get_vision_model_config` | Return config dict for vision model by name |
| `list_vision_models` | List registered vision model names |
| `run_variant_cleanup` | Run per-variant checkpoint cleanup |
| `run_final_cleanup` | Run final checkpoint prune at grid search end |
| `get_completed_count` | Count successful variants in results file |

## Dependencies

- **level_0**: Logging, config, paths, scoring, runtime
- **level_1**: Validation, pipelines, datasets, transforms, search
- **level_2**: Models, transforms, ensemble strategies, training, inference
- **level_3**: TTAPredictor
- **level_4**: File I/O, dataloaders, vision model creation
- **level_5**: BaseTabularModel, grid search persistence, metrics, metadata

## Usage Example

```python
from layers.layer_0_core.level_6 import (
    MLPModel,
    LogisticRegressionModel,
    create_variant_specific_data,
    create_variant_key,
    GridSearchBase,
    PredictPipeline,
)

# Create tabular model
model = LogisticRegressionModel(random_state=42)
model.fit(X_train, y_train)
proba = model.predict_proba(X_test)

# Variant key for grid search
variant_key = create_variant_key(
    config, preprocessing_list, augmentation_list, hyperparameters
)

# Prediction pipeline
pipeline = PredictPipeline(config, model_path="model.pkl", model_type="tabular")
pipeline.setup()
result = pipeline.execute()
```
