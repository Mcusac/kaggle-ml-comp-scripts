# level_1/features

## Purpose
Feature extraction infrastructure: extractor base class, feature cache configuration, filename encoding, registry mechanics, embedding fusion, physicochemical features, and lazy accessors for optional transformer models.

## Contents
- `base_feature_extractor.py` — `BaseFeatureExtractor`: abstract base with device setup and optional tqdm wrapping
- `cache/config.py` — runtime injection points for cache path provider and model ID map
- `cache/filename.py` — codec for encoding/decoding `(model_id, combo_id)` ↔ cache filename
- `feature_registry.py` — empty `INDIVIDUAL_FEATURES` and `FEATURE_PRESETS` dicts + lookup/parse functions; populated by higher layers
- `film.py` — `FiLM`: feature-wise linear modulation
- `fuse_embeddings.py` — align and concatenate multiple embeddings via level_0
- `physicochemical_features.py` — `calculate_physicochemical_properties`, `calculate_ctd_features`
- `siglip_classes.py` — lazy accessors for `transformers` library SigLIP classes

## Public API
- `BaseFeatureExtractor` — subclass and implement `extract_features()`
- `set_feature_cache_path_provider(provider)` — inject path provider at startup
- `set_model_id_map(model_id_map)` — inject model name → ID map at startup
- `get_cache_base_paths()` → `(input_base, working_base)`
- `get_model_name_from_model_id(model_id)` → model name string
- `get_metadata_dir()` → metadata directory path or None
- `generate_feature_filename(model_id, combo_id)` → filename string
- `parse_feature_filename(filename)` → `(model_id, combo_id)`
- `INDIVIDUAL_FEATURES`, `FEATURE_PRESETS` — mutable registry dicts
- `get_feature_preset(preset_name)`, `parse_feature_spec(feature_spec)`
- `FiLM` — feature-wise linear modulation layer
- `fuse_embeddings(embedding_list, target_ids)` → `(fused_array, common_ids)`
- `calculate_physicochemical_properties(sequence)`, `calculate_ctd_features(sequence)`
- `get_siglip_image_classes()`, `get_siglip_text_classes()` — return transformer classes or `(None, None)`

## Dependencies
- `level_0` — `get_logger`, `get_torch`, `align_embeddings`, `find_common_ids`, `AA_GROUPS`, `AA_WEIGHTS`, `HYDROPATHY_VALUES`
- `transformers` — optional; only imported if SigLIP accessors are called

## Usage Example
```python
from level_1.features import BaseFeatureExtractor, set_feature_cache_path_provider

set_feature_cache_path_provider(my_paths_callable)

class MyExtractor(BaseFeatureExtractor):
    def extract_features(self, dataset):
        ...
```