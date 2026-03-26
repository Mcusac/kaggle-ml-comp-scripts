# Contests package analysis

**On-disk root:** `scripts/layers/layer_1_competition/level_1_impl/` (packages `level_cafa`, `level_csiro`, `level_rna3d`, each with `level_0` … `level_K` folders).  
**Python imports:** `layers.layer_1_competition.level_1_impl.<contest>`.

**Scope:** CAFA, CSIRO, RNA3D contest trees  
**Date:** 2025-03-18  
**Constraints:** No refactoring, no abstraction, no code movement.

---

## Per competition

### 1. level_cafa (CAFA 6 Protein Function Prediction)

#### Structure
| Level | Files | Purpose |
|-------|-------|---------|
| level_0 | config, paths, data_schema, ontology, hierarchy, ontology_data_loader, ontology_model_manager, sequences, training, t5_loader, post_processor_goa_filter, threshold_optimization, per_ontology_labels, ontology_hyperparams, param_grid, parameter_grids | Base config, ontology system, data loaders, T5/RDS/QS embedding loaders |
| level_1 | embedding_paths, __init__ (re-exports GOAFilter) | Embedding path resolution, GOA filter |
| level_2 | post_processor, load_embeddings | Submission post-processing, embedding loading |
| level_3 | ontology_data_preparer | Feature/label preparation for per-ontology training |
| level_4 | per_ontology_training | Per-ontology training workflow |

#### Key Patterns
- **Ontology-centric:** F/P/C ontologies with per-ontology hyperparameters.
- **Hierarchy propagation:** GO hierarchy propagation via `HierarchyPropagator`; `CAFAHierarchy` wraps it.
- **GOA filtering:** Negative annotations from GOA filtered via `GOAFilter`; `propagate_negative_annotations`, `filter_submission_with_goa`.
- **Embedding loading:** `load_t5_rds`, `load_t5_qs` for R formats; `load_embedding_data` for numpy/T5; `embedding_paths.py` handles Kaggle vs local paths.
- **Per-ontology training:** `OntologyDataLoader` → `OntologyDataPreparer` → `OntologyModelManager`; sequential or parallel with GPU cleanup.
- **IA-weighted threshold optimization:** `optimize_threshold_ia_weighted`, `load_ia_weights` for hierarchical F1.
- **Parameter grids:** `param_grid.py` and `parameter_grids.py` both exist; `resolve_cafa_param_grid`, `get_ontology_param_grid`, `get_default_param_grid`.

#### Structural Issues
- **Duplicate param grid modules:** `param_grid.py` and `parameter_grids.py` overlap; `resolve_cafa_param_grid` vs `get_ontology_param_grid`.
- **GOAFilter location:** Defined in `level_0/post_processor_goa_filter.py` but re-exported from `level_1/__init__.py`; `post_processor.py` imports from `level_1`.
- **Placeholder implementations:** `per_ontology_labels.py` has `stream_labels` and `load_ontology_labels` as framework placeholders (warnings, empty returns).
- **sequences.py:** TODO notes it may be CAFA-specific; uses `normalize_protein_id` from shared competition infra (`layers.layer_1_competition.level_0_infra.level_0`).

#### Duplication Areas
- Ontology validation: `("F", "P", "C")` repeated in `param_grid.py`, `parameter_grids.py`, `training.py`, `config.py`.
- Hyperparameter resolution: `ontology_hyperparams.py` and `config.get_ontology_hyperparams` overlap.
- Per-ontology config: `CAFATrainingConfig.per_ontology_hyperparams` and `ontology_hyperparams.get_ontology_hyperparams`.

---

### 2. level_csiro (CSIRO Biomass Prediction)

#### Structure
| Level | Files | Purpose |
|-------|-------|---------|
| level_0 | config, paths, data_schema, metrics, biomass_models, model_resolution, handlers_common, csiro_grid_search_base, export_ops, config_setup, config_helper, oom_handlers, aggregate, model_constants, csiro_metadata, checkpoint_utils, stacking_utils | Base config, metrics, models, aggregation, OOM handling |
| level_1 | factory, modeling_shim, post_processor, stacking_helpers, e2e_ensemble_oof, train_pipeline, test_pipeline, meta_models, best_variant, model_selection, config_updater, load_gridsearch_metadata, apply_combo_to_config, extract_features_from_scratch | Model factory, post-processor, stacking, pipelines |
| level_2 | regression_training, stacking_pipeline, submit_best_variant_pipeline, submit_lightweight_pipeline, e2e_training, variant_selection, regression_ensemble_pipeline | Regression, stacking, submission, variant selection |
| level_3 | feature_extraction, grid_search_context, stacking_ensemble_pipeline, result_persistence, csiro_regression_ensemble, ensemble_pipeline | Feature extraction, grid search, ensemble |
| level_4 | regression_ensemble_oof, handlers_submit, handlers_grid_search, handlers_ensemble, train_and_export_pipeline | Handlers, train-and-export |
| level_5 | handlers_training, handlers_submit_best, multi_variant_regression_training_pipeline, hybrid_stacking_pipeline | Training handlers |
| level_6 | handlers_stacking, handlers_multi_variant | Stacking handlers |
| level_7 | handlers | CLI facade |

#### Key Patterns
- **Primary + derived targets:** 3 primary (Dry_Green_g, Dry_Clover_g, Dry_Dead_g) → 2 derived (GDM_g, Dry_Total_g); `compute_derived_targets` in config and metrics.
- **Constraint matrix post-processing:** `CSIROPostProcessor.apply` projects onto constraint subspace; `fixed_clover` mode; `target_specific_rules`.
- **Variant selection:** `metadata.json` + `gridsearch_metadata.json`; `get_regression_variant_info`, `find_best_regression_variant`, `get_or_create_regression_variant_id`, `save_regression_gridsearch_result`.
- **Feature extraction pipeline:** `aggregate_train_csv` → `create_train_dataloader` → `create_trainer` → `extract_all_features` → `save_features`.
- **Stacking:** `load_model_metadata`, `load_training_features`, `create_and_train_stacking_ensemble`; Ridge meta-model; OOF predictions.
- **Handler layering:** level_4/5/6 handlers; level_7 `get_handlers()` as facade; `CSIRO_COMMANDS` list.
- **OOM handling:** `handle_oom_error_with_retry` with batch size reduction, config injection.
- **Model factory:** `create_biomass_model(model_type, **params)`; `modeling_shim` for pickle compatibility.

#### Structural Issues
- **Deep handler hierarchy:** Handlers spread across level_4, 5, 6, 7; many small modules.
- **resolve_data_root vs resolve_data_root_from_args:** `handlers_common.resolve_data_root` delegates to `resolve_data_root_from_args`; naming inconsistency.
- **level_0 __init__ imports:** References `checkpoint_utils`, `csiro_metadata`, `stacking_utils` not yet seen in file list; possible missing files.
- **MODEL_ID_MAP:** `model_constants.py` has empty `MODEL_ID_MAP: dict[str, str] = {}` with TODO.

#### Duplication Areas
- `compute_derived_targets` logic in `config.py` and `metrics.py` (both implement green+clover+dead → gdm, total).
- Metadata load/merge logic: `variant_selection.py` has `_load_and_merge_variants`, `_load_and_merge_gridsearch_results`, `load_regression_gridsearch_results` with similar input/working dir merge patterns.
- `valid_types = {'lgbm', 'xgboost', 'ridge'}` repeated in multiple functions in `variant_selection.py`.
- Path resolution for Kaggle vs local: `str(input_metadata_dir).startswith('/kaggle/input')` pattern repeated.

---

### 3. level_rna3d (Stanford RNA 3D Folding Part 2)

#### Structure
| Level | Files | Purpose |
|-------|-------|---------|
| level_0 | config, paths, data_schema, post_processor, scoring, validate_data, artifacts, notebook_commands | Base config, TM-score, validation, artifacts |
| level_1 | baseline_approx | Template-based predictor, submission formatting |
| level_2 | model_registry, submission, tuning | Model registry, submit pipeline, tune pipeline |
| level_3 | training | Training orchestrator |
| level_4 | handlers | CLI handlers |

#### Key Patterns
- **Structure prediction:** 3D coordinates (x/y/z) for 5 structures per target; `build_coordinate_columns(n_structures=5)`.
- **TM-score metric:** Kabsch alignment, `_tm_score`, `evaluate_predictions_tm`; best-of-5 per target, max over ref conformations.
- **Baseline approximation:** `BaselineApproxPredictor` with template selection (global alignment), `_adapt_template_to_query`, `_apply_backbone_constraints`, `_fallback_structure`.
- **Submission strategies:** `submit_pipeline(strategy, models)` — single, ensemble, stacking; `_combine_predictions_average`, `_fit_stacking_weights`.
- **Model registry:** `get_trainer(model_name)`, `list_available_models()`; `_train_baseline_approx` builds template bank.
- **Tuning:** `tune_pipeline` with `_get_baseline_approx_grid` (quick/thorough); validation TM-score.
- **Notebook commands:** `build_validate_data_command`, `build_train_command`, `build_tune_command`, `build_submit_command` for run.py invocations.
- **Prediction artifacts:** `PredictionArtifact`, `save_prediction_artifact`, `load_prediction_artifact` for caching.

#### Structural Issues
- **Config minimalism:** `RNA3DConfig` returns empty lists/dicts for targets; `compute_derived_targets` is identity; framework target interface not a natural fit.
- **Duplicate config:** `level_0/config.py` exists but `level_0/__init__.py` imports from `.config`; `level_rna3d/__init__.py` imports from `level_0` — two config modules possible (one in level_0).
- **stacking_ensemble strategy:** `submit_pipeline` raises `NotImplementedError` for `stacking_ensemble`.

#### Duplication Areas
- `group_labels_to_coords` in `baseline_approx.py` and `_extract_reference_structures` in `scoring.py` both parse ID/resid and x_k/y_k/z_k columns.
- `run_baseline_approx_predictions` used by submission, tuning, and `make_submission`; good reuse.
- `format_predictions_to_submission_csv` and `_format_predictions_to_submission` — latter wraps former.

---

## Cross-Competition

### Shared Patterns (with file references)

| Pattern | CAFA | CSIRO | RNA3D |
|---------|------|-------|-------|
| **Contest registration** | `__init__.py`: `register_contest("cafa", ...)` | `__init__.py`: `register_contest("csiro", ..., training_data_loader=...)` | `__init__.py`: `register_contest("rna3d", ...)` |
| **Config base** | `level_0/config.py`: `CAFAConfig(ContestConfig)` | `level_0/config.py`: `CSIROConfig(ContestConfig)` | `level_0/config.py`: `RNA3DConfig(ContestConfig)` |
| **Paths base** | `level_0/paths.py`: `CAFAPaths(ContestPaths)` | `level_0/paths.py`: `CSIROPaths(ContestPaths)` | `level_0/paths.py`: `RNA3DPaths(ContestPaths)` |
| **Data schema base** | `level_0/data_schema.py`: `CAFADataSchema` | `level_0/data_schema.py`: `CSIRODataSchema` | `level_0/data_schema.py`: `RNA3DDataSchema` |
| **Post-processor base** | `level_2/post_processor.py`: `CAFAPostProcessor(ContestPostProcessor)` | `level_1/post_processor.py`: `CSIROPostProcessor(ContestPostProcessor)` | `level_0/post_processor.py`: `RNA3DPostProcessor(ClipRangePostProcessor)` |
| **compute_derived_targets** | Identity (no derived) | Primary→derived formula | Identity |
| **Handlers pattern** | — | `level_7/handlers.py`: `get_handlers()` | `level_4/handlers.py`: `get_handlers()` |
| **Train pipeline** | `level_4/per_ontology_training.py`: `PerOntologyTrainWorkflow.run_train_all` | `level_1/train_pipeline.py`, `level_2/regression_training.py` | `level_3/training.py`: `train_pipeline` |
| **Submit pipeline** | — | `level_2/submit_lightweight_pipeline`, `submit_best_variant_pipeline` | `level_2/submission.py`: `submit_pipeline` |
| **Tune pipeline** | — | Grid search (level_3/4) | `level_2/tuning.py`: `tune_pipeline` |
| **Validation** | `data_schema.validate_sample_id`, `validate_go_term` | `data_schema.validate_sample_id`, `parse_sample_id` | `level_0/validate_data.py`: `validate_rna3d_inputs` |
| **Kaggle vs local detection** | `embedding_paths.py`: `os.path.exists("/kaggle/input")` | `paths.py`: `Path('/kaggle/input').exists()` | — |

### Similar Function Signatures

| Signature | CAFA | CSIRO | RNA3D |
|-----------|------|-------|-------|
| `apply(predictions) -> predictions` | `CAFAPostProcessor.apply` | `CSIROPostProcessor.apply` | `RNA3DPostProcessor.apply` (via ClipRangePostProcessor) |
| `validate_sample_id(sample_id) -> bool` | `CAFADataSchema` | `CSIRODataSchema` | `RNA3DDataSchema` |
| `compute_derived_targets(predictions) -> predictions` | Identity | Formula | Identity |
| `get_handlers() -> Dict[str, Callable]` | — | `level_7/handlers.py` | `level_4/handlers.py` |
| `*_pipeline(data_root, ...)` | `PerOntologyTrainWorkflow.run_train_all` | `stacking_pipeline`, `submit_lightweight_pipeline` | `submit_pipeline`, `train_pipeline`, `tune_pipeline` |

### Parallel Structures

1. **Level 0 = base:** All have config, paths, data_schema in level_0; CAFA adds ontology/hierarchy; CSIRO adds metrics/aggregate; RNA3D adds scoring/artifacts.
2. **Post-processor placement:** CAFA level_2, CSIRO level_1, RNA3D level_0 — inconsistent.
3. **Handlers:** CSIRO has 4 handler levels (4–7); RNA3D has single level_4; CAFA has no explicit handlers.
4. **Training entry point:** CAFA `PerOntologyTrainWorkflow`; CSIRO `train_pipeline` (level_1) + `regression_training` (level_2); RNA3D `train_pipeline` (level_3).
5. **Submission entry point:** CAFA uses post-processor methods; CSIRO `submit_lightweight_pipeline`, `submit_best_variant_pipeline`; RNA3D `submit_pipeline`.

### Candidate Abstractions (NO implementation)

1. **ContestPipelineBase:** Common interface for `train_pipeline`, `submit_pipeline`, `tune_pipeline` with `(data_root, **kwargs)` pattern.
2. **HandlerRegistry:** `get_handlers() -> Dict[str, Callable]` with optional `extend_subparsers`; shared by CSIRO and RNA3D.
3. **PerTaskConfigResolver:** CAFA `per_ontology_hyperparams` and CSIRO variant hyperparameters both resolve config by task/variant key.
4. **MetadataMergePattern:** Input + working directory merge (CSIRO `variant_selection`) could be a generic `merge_json_from_input_and_working(input_path, working_path)`.
5. **EmbeddingLoaderProtocol:** `load_embedding_data(embedding_type, datatype, ...) -> (embeddings, ids)` — CAFA has full impl; CSIRO uses feature cache; RNA3D has no embeddings.
6. **ValidationOrchestrator:** `validate_*_inputs(data_root, ...)` pattern — RNA3D has explicit; CAFA/CSIRO use schema validate methods.
7. **GridSearchContextBuilder:** CSIRO `get_grid_search_context` builds context with metric, test_pipeline, metadata_handler; could be generic with contest-specific injectors.
8. **PostProcessorPlacement:** Standardize post-processor at level_1 or level_2 across contests.
9. **PathResolver:** Kaggle vs local detection (`/kaggle/input`), `get_data_root()`, `get_models_dir()` — shared helpers.
10. **DerivedTargetMixin:** `compute_derived_targets` with identity vs formula — could be mixin with override.

---

## Summary

- **CAFA:** Ontology-centric, embedding-heavy, GO hierarchy, per-ontology training; param grid and hyperparam resolution duplicated.
- **CSIRO:** Regression, variant metadata, stacking, feature extraction; deep handler hierarchy; metadata merge logic repeated.
- **RNA3D:** Structure prediction, TM-score, template baseline; minimal config; label/coordinate parsing duplicated with scoring.

Cross-competition: All follow `ContestConfig/Paths/DataSchema/PostProcessor` and `register_contest`. Handlers, pipelines, and validation patterns differ in structure and placement.
