# feature_extractors

Feature extraction implementations: backbone feature extraction, handcrafted protein features, and semantic text-probing features.

## Purpose

Provides concrete feature extractors that operate on DataLoaders or raw data and output numpy arrays. Cache I/O helpers are included for saving and loading extracted features to disk.

## Contents

- `cache_io.py` — Cache path resolution, feature save/load, cache lookup utilities
- `feature_extractor.py` — `FeatureExtractor`: single-pass backbone feature extraction from a PyTorch model
- `protein_feature_extractor.py` — `extract_handcrafted_features`: handcrafted physicochemical and k-mer features for protein sequences
- `semantic_features.py` — `SemanticFeatureExtractor`, `generate_semantic_features`: semantic score features from image embeddings via SigLIP text probing

## Public API

- `get_feature_cache_paths(filename)` — Return (input_path, working_path) for a cache filename
- `find_feature_cache(filename)` — Locate an existing feature cache file (session, input, or working dir)
- `save_features(all_features, all_targets, fold_assignments, filename, model_name, ...)` — Save extracted features to disk
- `load_features(cache_path)` — Load feature cache; returns (all_features, all_targets, fold_assignments, metadata)
- `resolve_extraction_info(feature_filename)` — Derive extraction metadata (model_name, model_id, combo_id, preprocessing_list, augmentation_list)
- `FeatureExtractor` — Extracts features from all batches in a DataLoader using a pretrained model backbone
- `extract_handcrafted_features(seq)` — Compute handcrafted protein features (k-mer frequencies, physicochemical) for a single sequence
- `SemanticFeatureExtractor` — Computes semantic similarity scores between image embeddings and text class labels
- `generate_semantic_features(image_embeddings, model_path, concept_groups, device)` — Convenience wrapper for semantic feature generation

## Dependencies

- **level_0** — `get_logger`, `get_torch`, `protein_features` constants, `prediction_guards` validators
- **level_1** — `BaseFeatureExtractor` (base class), `get_siglip_text_classes`, feature cache utilities

## Usage Example

```python
import torch
from level_2.feature_extractors import FeatureExtractor

model = ...  # pretrained PyTorch model
device = torch.device("cuda")
extractor = FeatureExtractor(model=model, device=device)
features = extractor.extract_features(dataloader, dataset_type="full")
# features: np.ndarray of shape (N, feature_dim)
```
