"""Semantic feature extraction via text probing.

Extracts features from image embeddings by computing cosine similarity
against text-encoded concept prompts. Domain-agnostic — concept groups
are injected at construction time.
"""

import numpy as np

from typing import Any, Dict, List, Optional, Union

from level_0 import get_logger, get_torch
from level_1 import BaseFeatureExtractor, get_siglip_text_classes

torch = get_torch()
logger = get_logger(__name__)


class SemanticFeatureExtractor(BaseFeatureExtractor):
    """
    Extract semantic features from image embeddings using text probing.

    Encodes a caller-supplied set of concept groups using the model's text
    encoder, then returns per-concept cosine similarities for each image
    embedding.

    Args:
        model_path: Path to a local SigLIP-compatible model.
        concept_groups: Mapping of concept name → list of text prompts.
        device: Torch device. Defaults to the base class default.
    """

    def __init__(
        self,
        model_path: str,
        concept_groups: Dict[str, List[str]],
        device: Optional[torch.device] = None,
    ):
        super().__init__(device=device)
        AutoModel, AutoTokenizer = get_siglip_text_classes()
        if AutoModel is None:
            raise RuntimeError(
                "transformers library not available. "
                "Install with: pip install transformers"
            )
        self.concept_groups = concept_groups

        logger.info(f"Loading model for semantic features from: {model_path}")
        logger.info(f"Using device: {self.device}")
        logger.info(f"Concept groups: {list(self.concept_groups.keys())}")

        try:
            self.model = AutoModel.from_pretrained(
                model_path, local_files_only=True
            ).to(self.device)
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_path, local_files_only=True
            )
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

        self.concept_vectors = self._encode_concepts()
        logger.info(f"Encoded {len(self.concept_vectors)} concept groups")

    def _encode_concepts(self) -> Dict[str, torch.Tensor]:
        """Encode all concept prompts into normalised mean text embeddings."""
        concept_vectors = {}
        with torch.no_grad():
            for name, prompts in self.concept_groups.items():
                inputs = self.tokenizer(
                    prompts,
                    padding="max_length",
                    return_tensors="pt",
                ).to(self.device)
                emb = self.model.get_text_features(**inputs)
                emb = emb / emb.norm(p=2, dim=-1, keepdim=True)
                concept_vectors[name] = emb.mean(dim=0, keepdim=True)
        return concept_vectors

    def extract_semantic_scores(
        self,
        image_embeddings: Union[np.ndarray, torch.Tensor],
    ) -> np.ndarray:
        """
        Compute cosine similarity between image embeddings and each concept.

        Args:
            image_embeddings: Shape (n_samples, embedding_dim).

        Returns:
            Array of shape (n_samples, n_concepts), columns ordered
            alphabetically by concept name.
        """
        if isinstance(image_embeddings, np.ndarray):
            img_tensor = torch.tensor(
                image_embeddings, dtype=torch.float32
            ).to(self.device)
        else:
            img_tensor = image_embeddings.to(self.device)

        img_tensor = img_tensor / img_tensor.norm(p=2, dim=-1, keepdim=True)
        scores = {}
        with torch.no_grad():
            for name, vec in self.concept_vectors.items():
                scores[name] = (
                    torch.matmul(img_tensor, vec.T).cpu().numpy().flatten()
                )

        concept_names = sorted(self.concept_groups.keys())
        return np.column_stack([scores[name] for name in concept_names])

    def extract_features(
        self,
        image_embeddings: Union[np.ndarray, torch.Tensor],
        **kwargs: Any,
    ) -> np.ndarray:
        """Implement BaseFeatureExtractor contract. Delegates to extract_semantic_scores."""
        return self.extract_semantic_scores(image_embeddings)

    def __call__(
        self,
        image_embeddings: Union[np.ndarray, torch.Tensor],
        **kwargs: Any,
    ) -> np.ndarray:
        return self.extract_features(image_embeddings, **kwargs)


def generate_semantic_features(
    image_embeddings: np.ndarray,
    model_path: str,
    concept_groups: Dict[str, List[str]],
    device: Optional[torch.device] = None,
) -> np.ndarray:
    """
    Convenience function: construct a SemanticFeatureExtractor and run it once.

    Args:
        image_embeddings: Shape (n_samples, embedding_dim).
        model_path: Path to a local SigLIP-compatible model.
        concept_groups: Mapping of concept name → list of text prompts.
        device: Torch device.

    Returns:
        Semantic score array of shape (n_samples, n_concepts).
    """
    return SemanticFeatureExtractor(
        model_path=model_path,
        concept_groups=concept_groups,
        device=device,
    )(image_embeddings)