"""SigLIP embedding extractor."""

import numpy as np

from PIL import Image
from pathlib import Path
from typing import Any, Callable, List, Optional, Tuple, Union

from level_0 import get_logger, get_torch, split_image, load_image_rgb
from level_1 import (
    BaseFeatureExtractor,
    get_siglip_image_classes,
    generate_feature_filename,
)
from level_2 import save_features

torch = get_torch()
logger = get_logger(__name__)

ModelResolver = Callable[[str], Tuple[str, Optional[str]]]


def _resolve_model_identity(
    model_path: str,
    model_name: Optional[str],
    model_id: Optional[str],
    model_resolver: Optional[ModelResolver],
) -> Tuple[str, Optional[str]]:
    """Resolve model_name and model_id from args or model_resolver."""
    if model_name is None and model_resolver is not None:
        model_name, resolved_id = model_resolver(model_path)
        if model_id is None:
            model_id = resolved_id

    if model_name is None:
        raise ValueError("model_name required or provide model_resolver")

    return model_name, model_id


def _load_siglip_components(
    model_path: str,
    device: torch.device,
    AutoModel: type,
    AutoImageProcessor: type,
) -> Tuple[Any, Any]:
    """Load SigLIP model and processor from local checkpoint."""
    logger.info(f"Loading SigLIP model: {model_path}")
    model = AutoModel.from_pretrained(
        model_path, local_files_only=True
    ).eval().to(device)
    processor = AutoImageProcessor.from_pretrained(
        model_path, local_files_only=True
    )
    return model, processor


def _detect_embedding_dim(model: Any) -> int:
    """Detect embedding dimension from model config."""
    if hasattr(model.config, "hidden_size"):
        return int(model.config.hidden_size)
    return 1152


class SigLIPExtractor(BaseFeatureExtractor):
    """SigLIP embedding extractor with patch aggregation.

    Loads a SigLIP model from a local checkpoint, splits each input image
    into overlapping patches, extracts per-patch embeddings, and returns
    their mean as a fixed-size feature vector.
    """

    def __init__(
        self,
        model_path: str,
        model_name: Optional[str] = None,
        model_id: Optional[str] = None,
        model_resolver: Optional[ModelResolver] = None,
        device: Optional[torch.device] = None,
        patch_size: int = 520,
        overlap: int = 16,
    ):
        """
        Initialize SigLIPExtractor.

        Args:
            model_path: Local path to a pretrained SigLIP model directory.
            model_name: Human-readable model name. Required unless model_resolver
                        is provided, in which case it is resolved automatically.
            model_id: Optional identifier used to name cache files. Resolved
                      from model_resolver when not provided.
            model_resolver: Optional callable that maps model_path to
                            (model_name, model_id). Used when model_name is None.
            device: Inference device. Defaults to BaseFeatureExtractor's device
                    resolution when None.
            patch_size: Size of each square image patch in pixels.
            overlap: Pixel overlap between adjacent patches.

        Raises:
            RuntimeError: If the transformers library is not installed.
            ValueError: If model_name cannot be determined from arguments.
        """
        super().__init__(device=device)

        AutoModel, AutoImageProcessor = get_siglip_image_classes()
        if AutoModel is None:
            raise RuntimeError(
                "transformers library not available. Install with: pip install transformers"
            )

        self.patch_size = patch_size
        self.overlap = overlap
        self.model_path = model_path

        self.model_name, self.model_id = _resolve_model_identity(
            model_path, model_name, model_id, model_resolver
        )

        self.model, self.processor = _load_siglip_components(
            model_path, self.device, AutoModel, AutoImageProcessor
        )

        self.embedding_dim = _detect_embedding_dim(self.model)

    def extract_from_image(
        self,
        image: Union[np.ndarray, Image.Image, str, Path],
        return_patches: bool = False,
    ) -> Union[np.ndarray, Tuple[np.ndarray, List[np.ndarray]]]:
        """
        Extract a single embedding from one image via patch aggregation.

        The image is split into overlapping patches of size patch_size. Each
        patch is embedded with the SigLIP model and the patch embeddings are
        averaged into a single vector.

        Args:
            image: Input image as a numpy array, PIL Image, file path string,
                   or Path object.
            return_patches: If True, also return the raw patch arrays alongside
                            the averaged embedding.

        Returns:
            If return_patches is False: float32 embedding array of shape
                (embedding_dim,).
            If return_patches is True: tuple of (embedding, patches), where
                patches is a list of numpy arrays.
        """
        img = load_image_rgb(image)

        patches = split_image(
            img,
            patch_size=self.patch_size,
            overlap=self.overlap,
        )

        patch_images = [Image.fromarray(p) for p in patches]

        with torch.no_grad():
            inputs = self.processor(images=patch_images, return_tensors="pt").to(self.device)
            features = self.model.get_image_features(**inputs)
            avg_embed = features.mean(dim=0).cpu().numpy()

        if return_patches:
            return avg_embed, patches

        return avg_embed

    def extract_batch(
        self,
        images: List[Union[np.ndarray, Image.Image, str, Path]],
        show_progress: bool = True,
    ) -> np.ndarray:
        """
        Extract embeddings for a list of images.

        Calls extract_from_image on each entry. Failed images are replaced
        with a zero vector of shape (embedding_dim,) and an error is logged.

        Args:
            images: List of images as numpy arrays, PIL Images, file paths,
                    or Path objects.
            show_progress: Whether to show a tqdm progress bar.

        Returns:
            Float32 array of shape (len(images), embedding_dim).
        """
        embeddings = []

        iterator = self._wrap_with_progress(
            images,
            desc="Extracting SigLIP embeddings",
            show_progress=show_progress,
        )

        for img in iterator:
            try:
                embeddings.append(self.extract_from_image(img))
            except Exception as e:
                logger.error(f"Image failed: {e}")
                embeddings.append(np.zeros(self.embedding_dim))

        return np.stack(embeddings)

    def extract_features(
        self,
        images: Union[List, np.ndarray, Image.Image, str, Path],
        **kwargs,
    ) -> np.ndarray:
        """
        Unified extraction entry point.

        Dispatches to extract_batch for list/tuple inputs and to
        extract_from_image for single inputs.

        Args:
            images: One image or a list of images.
            **kwargs: Forwarded to the dispatched method.

        Returns:
            Float32 embedding array of shape (embedding_dim,) for a single
            image, or (n_images, embedding_dim) for a list.
        """
        if isinstance(images, (list, tuple)):
            return self.extract_batch(images, **kwargs)
        return self.extract_from_image(images, **kwargs)

    def save_to_cache(
        self,
        all_features: np.ndarray,
        all_targets: np.ndarray,
        fold_assignments: np.ndarray,
        combo_id: str = "combo_00",
        dataset_type: str = "split",
    ) -> None:
        """
        Save extracted features to the project feature cache.

        Args:
            all_features: Feature array of shape (n_samples, embedding_dim).
            all_targets: Target array of shape (n_samples, n_targets).
            fold_assignments: Integer array of shape (n_samples,) with fold indices.
            combo_id: Identifier string appended to the cache filename.
            dataset_type: Dataset variant label stored in cache metadata.

        Raises:
            ValueError: If model_id was not set at construction time.
        """
        if self.model_id is None:
            raise ValueError("model_id required to save cache")

        filename = generate_feature_filename(self.model_id, combo_id)

        return save_features(
            all_features=all_features,
            all_targets=all_targets,
            fold_assignments=fold_assignments,
            filename=filename,
            model_name=self.model_name,
            dataset_type=dataset_type,
        )