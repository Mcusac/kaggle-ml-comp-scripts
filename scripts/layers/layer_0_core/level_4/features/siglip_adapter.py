"""SigLIP adapter to match FeatureExtractor interface (tensor in, tensor out)."""

from typing import Tuple
import numpy as np
from PIL import Image

from layers.layer_0_core.level_0 import get_torch
from layers.layer_0_core.level_3 import SigLIPExtractor

torch = get_torch()
nn = torch.nn


class SigLIPFeatureExtractorAdapter(nn.Module):
    """
    Adapter to make SigLIPExtractor compatible with FeatureExtractor interface.

    Converts PyTorch tensors to PIL Images and uses SigLIPExtractor.extract_from_image()
    to extract features, then returns them as tensors.
    """

    def __init__(self, siglip_extractor: SigLIPExtractor):
        super().__init__()
        self.siglip_extractor = siglip_extractor
        self.embedding_dim = siglip_extractor.embedding_dim
        model_name = siglip_extractor.model_name
        if '384' in model_name:
            self._input_size = (384, 384)
        elif '224' in model_name:
            self._input_size = (224, 224)
        else:
            self._input_size = (384, 384)

    def get_input_size(self) -> Tuple[int, int]:
        """Get input image size for this model."""
        return self._input_size

    def extract_features(self, x: torch.Tensor) -> torch.Tensor:
        """Extract features from batch of images [B, C, H, W] -> [B, embedding_dim]."""
        batch_size = x.shape[0]
        features_list = []
        for i in range(batch_size):
            img_tensor = x[i]
            img_np = img_tensor.permute(1, 2, 0).cpu().numpy()
            img_np = np.clip(img_np, 0, 1)
            img_np = (img_np * 255).astype(np.uint8)
            img_pil = Image.fromarray(img_np)
            features = self.siglip_extractor.extract_from_image(img_pil, return_patches=False)
            features_list.append(features)
        return torch.from_numpy(np.stack(features_list)).float()
