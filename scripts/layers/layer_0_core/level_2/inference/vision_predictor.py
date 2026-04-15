"""Vision model predictor for inference."""

import numpy as np

from tqdm import tqdm

from layers.layer_0_core.level_0 import get_logger, get_torch
from layers.layer_0_core.level_1 import forward_with_amp

torch = get_torch()
nn = torch.nn
DataLoader = torch.utils.data.DataLoader

logger = get_logger(__name__)


class VisionPredictor:
    """Batch prediction on vision datasets with optional progress tracking."""

    def __init__(
        self,
        model: nn.Module,
        device: torch.device,
        use_mixed_precision: bool = False,
    ):
        self.model = model.to(device)
        self.model.eval()
        self.device = device
        self.use_mixed_precision = use_mixed_precision
        if self.use_mixed_precision:
            logger.info("Mixed precision (FP16) inference enabled")

    @torch.no_grad()
    def predict(
        self,
        dataloader: DataLoader,
        verbose: bool = True,
    ) -> np.ndarray:
        """
        Generate predictions for an entire dataset.

        Args:
            dataloader: DataLoader to iterate over.
            verbose: Show tqdm progress bar (default: True).

        Returns:
            Predictions array of shape (n_samples, n_outputs).
        """
        all_preds = []
        iterator = tqdm(dataloader, desc="Predicting") if verbose else dataloader

        for batch in iterator:
            if isinstance(batch, (list, tuple)):
                # First element is always images; remaining elements (labels etc.)
                # are intentionally dropped — this is inference-only.
                images = batch[0]
            else:
                images = batch

            images = images.to(self.device)
            outputs = forward_with_amp(self.model, images, self.use_mixed_precision)
            all_preds.append(outputs.cpu().numpy())

        predictions = np.concatenate(all_preds, axis=0)
        logger.info(f"Generated {len(predictions)} predictions")
        return predictions

    @torch.no_grad()
    def predict_single(self, image: torch.Tensor) -> np.ndarray:
        """
        Predict on a single image tensor.

        Args:
            image: Tensor of shape (C, H, W) or (1, C, H, W).

        Returns:
            Prediction array of shape (n_outputs,).
        """
        if image.dim() == 3:
            image = image.unsqueeze(0)
        image = image.to(self.device)
        return forward_with_amp(self.model, image, self.use_mixed_precision).cpu().numpy()[0]