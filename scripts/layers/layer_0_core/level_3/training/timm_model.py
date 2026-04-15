"""Wrapper for timm models with configurable output head."""

# NOTE: forward_features() is used instead of __call__ to make the intent
# explicit (feature extraction, not classification). The backbone is created
# with num_classes=0, which already removes the classifier; this makes the
# contract visible in the code.

from typing import Any, Literal, Optional, Tuple, Union

from layers.layer_0_core.level_0 import get_logger, get_torch
from layers.layer_0_core.level_1 import BaseVisionModel
from layers.layer_0_core.level_2 import TimmWeightLoader

logger = get_logger(__name__)
torch = get_torch()
nn = torch.nn

DEFAULT_IMAGE_SIZE: Tuple[int, int] = (224, 224)

DatasetType = Literal['single', 'split']


class TimmModel(BaseVisionModel):
    """Wrapper for timm models with configurable regression head.

    Two dataset types are supported, selected at construction time:
      'single' — each forward pass receives one image tensor; uses head_single.
      'split'  — each forward pass receives a (left, right) image tuple;
                 uses head_split with cross-gating between the two streams.

    Only the head required for the chosen dataset_type is created, saving
    memory and parameters for every model instance.
    """

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def _validate_init_params(
        self,
        model_name: str,
        num_classes: int,
        input_size: Optional[Tuple[int, int]],
    ) -> None:

        if not isinstance(model_name, str) or not model_name:
            raise ValueError(f"model_name must be non-empty string, got {model_name}")

        if not isinstance(num_classes, int) or num_classes < 1:
            raise ValueError(f"num_classes must be positive integer, got {num_classes}")

        if input_size is not None:
            if not isinstance(input_size, (tuple, list)) or len(input_size) != 2:
                raise ValueError(
                    f"input_size must be (height, width), got {input_size}"
                )

            h, w = input_size
            if not isinstance(h, int) or not isinstance(w, int):
                raise ValueError(
                    f"input_size dimensions must be integers, got {input_size}"
                )

            if h < 1 or w < 1:
                raise ValueError(
                    f"input_size dimensions must be positive, got {input_size}"
                )

    # ------------------------------------------------------------------
    # Backbone
    # ------------------------------------------------------------------

    def _create_backbone(self, model_name: str, pretrained: bool) -> tuple:

        logger.info(f"Creating timm model: {model_name} (pretrained={pretrained})")

        weight_loader = TimmWeightLoader()

        backbone = weight_loader.load_weights(
            model_name=model_name,
            num_classes=0,
            pretrained=pretrained,
        )

        pretrained_loaded = weight_loader.is_pretrained_loaded()

        return backbone, pretrained_loaded

    # ------------------------------------------------------------------
    # Feature dimension
    # ------------------------------------------------------------------

    def _extract_feature_dimension(self, backbone: Any) -> int:
        """
        Determine backbone output feature dimension.

        Uses timm conventions instead of fragile dummy inference.
        """

        if hasattr(backbone, "num_features"):
            return int(backbone.num_features)

        if hasattr(backbone, "num_classes"):
            return int(backbone.num_classes)

        logger.warning(
            "Could not determine feature dimension from backbone attributes. "
            "Falling back to default 2048."
        )

        return 2048

    # ------------------------------------------------------------------
    # Regression heads
    # ------------------------------------------------------------------

    def _create_regression_heads(self, num_classes: int) -> None:
        """
        Create only the regression head required by dataset_type.

        'single': creates head_single (feat_dim → num_classes).
        'split':  creates head_split (feat_dim*2 → num_classes) plus
                  cross_gate_left and cross_gate_right attention layers.
        """
        if self.dataset_type == 'split':
            hidden_split = max(32, int(self.feat_dim * 2 * 0.25))

            self.head_split = nn.Sequential(
                nn.Linear(self.feat_dim * 2, hidden_split),
                nn.ReLU(inplace=True),
                nn.Dropout(0.3),
                nn.Linear(hidden_split, num_classes),
            )

            self.cross_gate_left = nn.Linear(self.feat_dim, self.feat_dim)
            self.cross_gate_right = nn.Linear(self.feat_dim, self.feat_dim)

        else:
            hidden_size = max(32, int(self.feat_dim * 0.25))

            self.head_single = nn.Sequential(
                nn.Linear(self.feat_dim, hidden_size),
                nn.ReLU(inplace=True),
                nn.Dropout(0.3),
                nn.Linear(hidden_size, num_classes),
            )

    # ------------------------------------------------------------------
    # Input size
    # ------------------------------------------------------------------

    def _extract_input_size(
        self,
        backbone: Any,
        input_size: Optional[Tuple[int, int]],
    ) -> Tuple[int, int]:

        if input_size is not None:
            return tuple(input_size)

        try:
            cfg = getattr(backbone, "pretrained_cfg", None)

            if isinstance(cfg, dict) and "input_size" in cfg:
                size = cfg["input_size"]

                if isinstance(size, (list, tuple)) and len(size) >= 2:
                    return (size[-2], size[-1])

        except Exception as e:
            logger.warning(f"Error reading pretrained_cfg input_size: {e}")

        return DEFAULT_IMAGE_SIZE

    # ------------------------------------------------------------------
    # Init
    # ------------------------------------------------------------------

    def __init__(
        self,
        model_name: str = "efficientnet_b0",
        pretrained: bool = True,
        num_classes: int = 1,
        input_size: Optional[Tuple[int, int]] = None,
        dataset_type: DatasetType = 'single',
    ):
        """
        Initialize TimmModel.

        Args:
            model_name: timm model identifier (e.g. 'efficientnet_b0').
            pretrained: Whether to load pretrained weights.
            num_classes: Number of output targets.
            input_size: Override image input size as (height, width).
                        Inferred from backbone pretrained_cfg when None.
            dataset_type: Controls which regression head is created.
                'single' — one image per sample; uses head_single.
                'split'  — (left, right) image pair per sample; uses head_split.
        """
        super().__init__()

        self._validate_init_params(model_name, num_classes, input_size)

        self.model_name = model_name
        self.num_classes = num_classes
        self.dataset_type = dataset_type

        self.backbone, self._pretrained_loaded = self._create_backbone(
            model_name,
            pretrained,
        )

        self.feat_dim = self._extract_feature_dimension(self.backbone)

        logger.info(f"Backbone feature dimension: {self.feat_dim}")

        self._create_regression_heads(num_classes)

        self.input_size = self._extract_input_size(self.backbone, input_size)

        logger.info(f"Model input size: {self.input_size}")

    # ------------------------------------------------------------------
    # Forward
    # ------------------------------------------------------------------

    def forward(
        self,
        x: Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]],
    ) -> torch.Tensor:

        if isinstance(x, tuple):
            if self.dataset_type != 'split':
                raise RuntimeError(
                    f"TimmModel was created with dataset_type='{self.dataset_type}'; "
                    "cannot forward a split-image tuple. "
                    "Re-initialise with dataset_type='split'."
                )

            left_img, right_img = x

            left_feat = self.backbone.forward_features(left_img)
            right_feat = self.backbone.forward_features(right_img)

            g_l = torch.sigmoid(self.cross_gate_left(right_feat))
            g_r = torch.sigmoid(self.cross_gate_right(left_feat))

            left_feat = left_feat * g_l
            right_feat = right_feat * g_r

            combined = torch.cat([left_feat, right_feat], dim=1)

            return self.head_split(combined)

        if self.dataset_type == 'split':
            raise RuntimeError(
                "TimmModel was created with dataset_type='split'; "
                "cannot forward a single image tensor. "
                "Pass a (left, right) tuple or re-initialise with dataset_type='single'."
            )

        features = self.backbone.forward_features(x)

        return self.head_single(features)

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def get_input_size(self) -> Tuple[int, int]:
        return self.input_size

    def freeze_backbone(self) -> None:

        for p in self.backbone.parameters():
            p.requires_grad = False

        logger.info(f"Frozen {self.model_name} backbone")

    def unfreeze_backbone(self) -> None:

        for p in self.backbone.parameters():
            p.requires_grad = True

        logger.info(f"Unfrozen {self.model_name} backbone")

    def is_pretrained(self) -> bool:
        return self._pretrained_loaded