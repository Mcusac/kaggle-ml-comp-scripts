"""Extract features from model backbone; no TTA."""

from typing import Tuple

import numpy as np

from layers.layer_0_core.level_0 import get_logger, get_torch
from layers.layer_0_core.level_1 import BaseFeatureExtractor

_torch = get_torch()
_DataLoader = _torch.utils.data.DataLoader
_logger = get_logger(__name__)


class FeatureExtractor(BaseFeatureExtractor):
    """Extract features from model (backbone / _extract_hf_features). Single-pass only, no TTA."""

    def __init__(self, model: _torch.nn.Module, device: _torch.device):
        super().__init__(device=device)
        self.model = model
        self.model.eval()
        self.model.to(self.device)

    def extract_features(
        self,
        dataloader: _DataLoader,
        dataset_type: str = 'split',
    ) -> np.ndarray:
        """Extract features from all batches. dataset_type 'full' or 'split'."""
        return self._extract_features_single_pass(dataloader, dataset_type)

    def extract_features_and_targets(
        self,
        dataloader: _DataLoader,
        dataset_type: str = 'split',
    ) -> Tuple[np.ndarray, np.ndarray]:
        """Extract features and targets from all batches. Returns (features, targets)."""
        all_features = []
        all_targets = []
        with _torch.no_grad():
            for batch in dataloader:
                if dataset_type == 'split':
                    left_img, right_img, targets = batch
                    left_img = left_img.to(self.device)
                    right_img = right_img.to(self.device)
                    left_feat = self._extract_from_model(left_img)
                    right_feat = self._extract_from_model(right_img)
                    features = _torch.cat([left_feat, right_feat], dim=1)
                else:
                    images, targets = batch
                    images = images.to(self.device)
                    features = self._extract_from_model(images)
                all_features.append(features.cpu().numpy())
                t = targets.cpu().numpy() if hasattr(targets, 'cpu') else np.array(targets)
                all_targets.append(t)
        return (
            np.concatenate(all_features, axis=0),
            np.concatenate(all_targets, axis=0),
        )

    def _extract_features_single_pass(
        self,
        dataloader: _DataLoader,
        dataset_type: str,
    ) -> np.ndarray:
        all_features = []
        with _torch.no_grad():
            for batch in dataloader:
                if dataset_type == 'split':
                    left_img, right_img, _ = batch
                    left_img = left_img.to(self.device)
                    right_img = right_img.to(self.device)
                    left_feat = self._extract_from_model(left_img)
                    right_feat = self._extract_from_model(right_img)
                    features = _torch.cat([left_feat, right_feat], dim=1)
                else:
                    images, _ = batch
                    images = images.to(self.device)
                    features = self._extract_from_model(images)
                all_features.append(features.cpu().numpy())
        return np.concatenate(all_features, axis=0)

    def _extract_from_model(self, x: _torch.Tensor) -> _torch.Tensor:
        """Dispatch to model feature extraction; supports _extract_hf_features, extract_features, or backbone."""
        if hasattr(self.model, '_extract_hf_features'):
            return self.model._extract_hf_features(x)
        if hasattr(self.model, 'extract_features'):
            return self.model.extract_features(x)
        if hasattr(self.model, 'backbone'):
            b = self.model.backbone
            if hasattr(b, '_extract_hf_features'):
                return b._extract_hf_features(x)
            out = b(x)
            if hasattr(out, 'last_hidden_state'):
                h = out.last_hidden_state
                cls_t = h[:, 0, :]
                pt = h[:, 1:, :]
                return _torch.cat([cls_t, pt.mean(dim=1), pt.max(dim=1)[0]], dim=1)
            return out
        raise RuntimeError(
            f"Cannot extract features from {type(self.model)}. "
            "Model must implement extract_features() via BaseFeatureExtractor, "
            "or expose _extract_hf_features() or .backbone."
        )