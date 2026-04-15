"""Noise addition augmentations. Callers pass params (e.g. from contest transform_defaults)."""

from layers.layer_0_core.level_0 import (
    get_logger,
    get_nn_module_base_class,
    get_torch,
    get_vision_module_and_tensor_types,
)

torch = get_torch()
_NNModule = get_nn_module_base_class()
_, TensorT = get_vision_module_and_tensor_types()
logger = get_logger(__name__)


class AddGaussianNoise(_NNModule):
    """
    Add Gaussian noise to tensor images (apply after ToTensor()).
    Optional probability p for random application; output clipped to [0, 1].
    """

    def __init__(self, mean: float = 0.0, std: float = 0.01, p: float = 1.0):
        super().__init__()
        if std < 0:
            raise ValueError(f"std must be non-negative, got {std}")
        self.mean = mean
        self.std = std
        self.p = p

    def forward(self, tensor: TensorT) -> TensorT:
        if torch is None:
            raise RuntimeError("PyTorch is required for AddGaussianNoise.")
        if self.p < 1.0 and torch.rand(1, device=tensor.device).item() >= self.p:
            return tensor
        noise = torch.randn_like(tensor) * self.std + self.mean
        return torch.clamp(tensor + noise, 0.0, 1.0)

    def __repr__(self):
        return f"{self.__class__.__name__}(mean={self.mean}, std={self.std}, p={self.p})"


def get_noise_transform(
    mean: float = 0.0,
    std: float = 0.01,
    p: float = 1.0,
):
    """
    Get Gaussian noise addition transform. Caller passes params (contest may use its defaults).
    """
    return AddGaussianNoise(mean=mean, std=std, p=p)
