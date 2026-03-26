"""Feature extraction model creation (SigLIP, DINOv2, timm). Uses level_0, level_3, level_4."""

from typing import Optional, Tuple, Callable

from layers.layer_0_core.level_0 import get_logger, get_torch
from layers.layer_0_core.level_3 import SigLIPExtractor
from layers.layer_0_core.level_4 import create_vision_model, SigLIPFeatureExtractorAdapter

from layers.layer_1_competition.level_0_infra.level_0 import get_pretrained_weights_path

logger = get_logger(__name__)

torch = get_torch()
nn = torch.nn

# Optional: set via set_pretrained_weights_resolver() by contest/orchestration for SigLIP.
_pretrained_weights_resolver: Optional[Callable[[str], str]] = None


def set_pretrained_weights_resolver(resolver: Optional[Callable[[str], str]]) -> None:
    """Set callable that returns pretrained weights path for a model name (e.g. SigLIP)."""
    global _pretrained_weights_resolver
    _pretrained_weights_resolver = resolver


def create_feature_extraction_model(
    model_name: str,
    num_primary_targets: int,
    device: torch.device,
    image_size: Optional[Tuple[int, int]] = None,
    pretrained: bool = True
) -> nn.Module:
    """
    Create feature extraction model, handling all model types (SigLIP, DINOv2, timm).

    Args:
        model_name: Model name (e.g., 'siglip_so400m_patch14_384', 'dinov2_base', 'timm_efficientnet_b3')
        num_primary_targets: Number of primary targets (for DINOv2/timm models)
        device: Device to run model on
        image_size: Optional image size override
        pretrained: Whether to load pretrained weights

    Returns:
        Feature extraction model:
        - SigLIPFeatureExtractorAdapter for SigLIP models
        - DINOv2Model or TimmModel for other models
    """
    model_name_lower = model_name.lower()
    is_siglip = "siglip" in model_name_lower

    if is_siglip:
        if _pretrained_weights_resolver is None:
            try:
                model_path = get_pretrained_weights_path(model_name)
            except ImportError:
                raise RuntimeError(
                    "SigLIP requires a pretrained weights path. "
                    "Set components.features.set_pretrained_weights_resolver(...) "
                    "or install contest config with get_pretrained_weights_path."
                )
        else:
            model_path = _pretrained_weights_resolver(model_name)
        siglip_extractor = SigLIPExtractor(
            model_path=model_path,
            model_name=model_name,
            device=device
        )
        model = SigLIPFeatureExtractorAdapter(siglip_extractor)
        logger.info(f"Created SigLIP feature extraction model: {model_name}")
        return model
    else:
        model = create_vision_model(
            model_name=model_name,
            num_classes=num_primary_targets,
            pretrained=pretrained,
            input_size=image_size,
        )
        logger.info(f"Created vision feature extraction model: {model_name}")
        return model
