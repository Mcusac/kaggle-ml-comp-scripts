"""Biomass-specific semantic feature extraction.

Subclasses SemanticFeatureExtractor with pasture/biomass concept groups
and domain-specific ratio features. CSIRO biomass domain.
"""

import numpy as np

from typing import Any, Optional, Union

from layers.layer_0_core.level_0 import get_torch
from layers.layer_0_core.level_2 import SemanticFeatureExtractor

torch = get_torch()

BIOMASS_CONCEPT_GROUPS = {
    "bare":   ["bare soil", "dirt ground", "sparse vegetation", "exposed earth"],
    "sparse": ["low density pasture", "thin grass", "short clipped grass"],
    "medium": ["average pasture cover", "medium height grass", "grazed pasture"],
    "dense":  ["dense tall pasture", "thick grassy volume", "high biomass", "overgrown vegetation"],
    "green":  ["lush green vibrant pasture", "photosynthesizing leaves", "fresh growth"],
    "dead":   ["dry brown dead grass", "yellow straw", "senesced material", "standing hay"],
    "clover": ["white clover", "trifolium repens", "broadleaf legume", "clover flowers"],
    "grass":  ["ryegrass", "blade-like leaves", "fescue", "grassy sward"],
}

_EPSILON = 1e-6


class BiomassSemanticFeatureExtractor(SemanticFeatureExtractor):
    """
    Semantic feature extractor for pasture biomass estimation.

    Extends SemanticFeatureExtractor with BIOMASS_CONCEPT_GROUPS and adds
    three domain-specific ratio features:
        - greenness  : green / (green + dead)
        - clover     : clover / (clover + grass)
        - cover      : (dense + medium) / (bare + sparse)

    Args:
        model_path: Path to a local SigLIP-compatible model.
        device: Torch device. Defaults to the base class default.
    """

    def __init__(
        self,
        model_path: str,
        device: Optional[torch.device] = None,
    ):
        super().__init__(
            model_path=model_path,
            concept_groups=BIOMASS_CONCEPT_GROUPS,
            device=device,
        )
        # Pre-compute stable column index map from sorted concept names
        self._concept_idx = {
            name: i for i, name in enumerate(sorted(BIOMASS_CONCEPT_GROUPS.keys()))
        }

    def _compute_ratios(self, scores: np.ndarray) -> np.ndarray:
        """Compute the three biomass ratio features from concept scores."""
        idx = self._concept_idx
        green  = scores[:, idx["green"]]
        dead   = scores[:, idx["dead"]]
        clover = scores[:, idx["clover"]]
        grass  = scores[:, idx["grass"]]
        dense  = scores[:, idx["dense"]]
        medium = scores[:, idx["medium"]]
        bare   = scores[:, idx["bare"]]
        sparse = scores[:, idx["sparse"]]

        ratio_greenness = green  / (green  + dead   + _EPSILON)
        ratio_clover    = clover / (clover + grass  + _EPSILON)
        ratio_cover     = (dense + medium) / (bare + sparse + _EPSILON)

        return np.column_stack([ratio_greenness, ratio_clover, ratio_cover])

    def extract_features(
        self,
        image_embeddings: Union[np.ndarray, torch.Tensor],
        include_ratios: bool = True,
        **kwargs: Any,
    ) -> np.ndarray:
        """
        Extract semantic scores and optionally append ratio features.

        Args:
            image_embeddings: Shape (n_samples, embedding_dim).
            include_ratios: If True (default), append the three biomass ratio
                columns to the semantic scores.

        Returns:
            Shape (n_samples, n_concepts) when include_ratios=False.
            Shape (n_samples, n_concepts + 3) when include_ratios=True.
        """
        scores = self.extract_semantic_scores(image_embeddings)
        if not include_ratios:
            return scores
        return np.hstack([scores, self._compute_ratios(scores)])


def generate_biomass_semantic_features(
    image_embeddings: np.ndarray,
    model_path: str,
    device: Optional[torch.device] = None,
    include_ratios: bool = True,
) -> np.ndarray:
    """
    Convenience function for one-shot biomass semantic feature extraction.

    Args:
        image_embeddings: Shape (n_samples, embedding_dim).
        model_path: Path to a local SigLIP-compatible model.
        device: Torch device.
        include_ratios: Append ratio features (default True).

    Returns:
        Feature array of shape (n_samples, n_concepts[+ 3]).
    """
    return BiomassSemanticFeatureExtractor(
        model_path=model_path,
        device=device,
    ).extract_features(image_embeddings, include_ratios=include_ratios)
