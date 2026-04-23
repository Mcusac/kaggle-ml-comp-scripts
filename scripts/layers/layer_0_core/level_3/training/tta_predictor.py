"""Test-time augmentation predictor."""

import numpy as np

from PIL import Image
from typing import List, Optional, Union
from tqdm import tqdm

from layers.layer_0_core.level_0 import get_logger, get_torch
from layers.layer_0_core.level_1 import forward_with_amp
from layers.layer_0_core.level_2 import TTAVariant, build_tta_transforms

_torch = get_torch()
_nn = _torch.nn
_DataLoader = _torch.utils.data.DataLoader
_logger = get_logger(__name__)


class TTAPredictor:
    """
    Test-time augmentation predictor.

    Applies multiple augmentation variants to each test image and averages
    the predictions for improved robustness.
    """

    def __init__(
        self,
        model: _nn.Module,
        device: _torch.device,
        image_size: int = 224,
        tta_variants: Optional[List[Union[TTAVariant, str]]] = None,
        use_mixed_precision: bool = False,
    ):
        """
        Initialize TTA Predictor.

        Args:
            model: Model to run inference with. Moved to device on init.
            device: Device to run inference on.
            image_size: Input image size passed to build_tta_transforms.
            tta_variants: TTA variant list. Uses build_tta_transforms defaults when None.
            use_mixed_precision: Whether to use FP16 inference via autocast.
        """
        self.model = model.to(device)
        self.model.eval()
        self.device = device
        self.use_mixed_precision = use_mixed_precision

        self.tta_transforms = build_tta_transforms(
            image_size=image_size,
            variants=tta_variants,
        )

        _logger.info(f"TTA Predictor initialized with {len(self.tta_transforms)} variants")

        if self.use_mixed_precision:
            _logger.info("Mixed precision (FP16) inference enabled")

    @_torch.no_grad()
    def predict(
        self,
        dataloader: _DataLoader,
        verbose: bool = True,
    ) -> np.ndarray:
        """
        Generate TTA predictions for a full dataset.

        Each batch is passed through all TTA transforms independently.
        Predictions across variants are averaged per sample.

        Args:
            dataloader: DataLoader yielding batches of image tensors.
                        Batches may be plain tensors or (images, ...) tuples;
                        the first element is taken as the image tensor.
            verbose: Whether to show a tqdm progress bar.

        Returns:
            Float32 array of shape (n_samples, n_outputs) with averaged predictions.
        """
        all_preds = []
        iterator = tqdm(dataloader, desc="TTA Prediction") if verbose else dataloader

        for batch in iterator:
            if isinstance(batch, (list, tuple)):
                images = batch[0] if len(batch) > 1 else batch
            else:
                images = batch

            variant_preds = []

            for transform in self.tta_transforms:
                transformed_images = transform(images).to(self.device)
                outputs = forward_with_amp(self.model, transformed_images, self.use_mixed_precision)
                variant_preds.append(outputs.cpu().numpy())

            avg_pred = np.mean(variant_preds, axis=0)
            all_preds.append(avg_pred)

        predictions = np.concatenate(all_preds, axis=0)

        _logger.info(f"Generated TTA predictions for {len(predictions)} samples")
        _logger.info(f"  Averaged across {len(self.tta_transforms)} TTA variants")

        return predictions

    def predict_single_image(
        self,
        image: _torch.Tensor,
        pil_image: Optional[Image.Image] = None,
    ) -> np.ndarray:
        """
        Predict on a single image with TTA.

        When pil_image is provided, each TTA transform is applied to it
        individually and the results are averaged. When only a pre-processed
        tensor is provided, TTA cannot be applied (transforms expect PIL input);
        the tensor is forwarded directly and the result is returned as-is.

        Args:
            image: Pre-processed image tensor of shape (C, H, W) or (1, C, H, W).
            pil_image: Optional PIL image. When provided, TTA transforms are applied.

        Returns:
            Float32 array of shape (n_outputs,) with averaged predictions.
        """
        variant_preds = []

        if pil_image is not None:
            for transform in self.tta_transforms:
                transformed = transform(pil_image)
                if transformed.dim() == 3:
                    transformed = transformed.unsqueeze(0)
                transformed = transformed.to(self.device)
                output = forward_with_amp(self.model, transformed, self.use_mixed_precision)
                variant_preds.append(output.cpu().numpy()[0])
        else:
            if image.dim() == 3:
                image = image.unsqueeze(0)
            image = image.to(self.device)
            output = forward_with_amp(self.model, image, self.use_mixed_precision)
            variant_preds.append(output.cpu().numpy()[0])

        return np.mean(variant_preds, axis=0)