# level_3 features

## Purpose

Feature extraction pipelines for vision and protein sequence data, including SigLIP embeddings, handcrafted biochemical features, a supervised dimensionality-reduction engine, and a bulk extraction loop.

## Contents

- `siglip_extractor.py` — `SigLIPExtractor`: loads a SigLIP model, splits images into overlapping patches, and returns mean patch embeddings with optional cache saving.
- `supervised_embedding_engine.py` — `SupervisedEmbeddingEngine`: scikit-learn pipeline combining StandardScaler, PCA, PLSRegression, and GaussianMixture into a single fit/transform interface.
- `handcrafted_feature_extraction.py` — `extract_handcrafted_features_for_ids`, `extract_handcrafted_parallel`, `stream_features`: sequential, parallel (thread pool), and memory-safe chunked extraction of biochemical features for protein IDs.
- `extract_all_features.py` — `extract_all_features`: drains a DataLoader through a `FeatureExtractor` and returns stacked feature and target arrays.

## Public API

- `SigLIPExtractor` — patch-based SigLIP embedding extractor with `extract_features`, `extract_batch`, `extract_from_image`, and `save_to_cache` methods.
- `SupervisedEmbeddingEngine` — PCA + PLS + GMM pipeline with `fit`, `transform`, and `fit_transform` methods.
- `extract_handcrafted_features_for_ids(sequences, protein_ids)` — sequential extraction for an ordered list of protein IDs.
- `extract_handcrafted_parallel(sequences, protein_ids, max_workers)` — thread-parallel version of the above.
- `stream_features(sequences, chunk_size)` — generator yielding `(feature_matrix, protein_ids)` chunks for memory-efficient processing.
- `extract_all_features(feature_extractor, all_loader, dataset_type)` — extract features and targets from a full DataLoader. Expects a level_2 `FeatureExtractor` (dataloader-based); `SigLIPExtractor` uses images directly and is not compatible.

## Dependencies

- **level_0** — `get_logger`, `get_torch`, `split_image`, `load_image_rgb`, `HANDCRAFTED_FEATURE_DIM`.
- **level_1** — `BaseFeatureExtractor` (base class for `SigLIPExtractor`), `get_siglip_image_classes` (lazy transformer class loader), `generate_feature_filename`.
- **level_2** — `save_features` (feature cache persistence), `extract_handcrafted_features` (per-sequence biochemical feature computation), `FeatureExtractor` (passed as argument to `extract_all_features`), `get_standard_scaler`, `get_pca`, `get_pls_regression`, `get_gaussian_mixture`.

## Usage Example

```python
from layers.layer_0_core.level_3.features import SigLIPExtractor, extract_handcrafted_features_for_ids

extractor = SigLIPExtractor(
    model_path="/models/siglip",
    model_name="siglip-so400m",
    model_id="siglip_v1",
    patch_size=520,
)
embedding = extractor.extract_from_image("photo.jpg")

features = extract_handcrafted_features_for_ids(
    sequences={"P12345": "MKTAYIAKQRQISFVKSHFSRQ"},
    protein_ids=["P12345"],
)
```
