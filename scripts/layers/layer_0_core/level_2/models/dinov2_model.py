"""DINOv2 model wrapper for vision tasks."""

import warnings

from typing import Tuple, Optional, Union
from transformers import Dinov2Model as HFDinov2Model

from level_0 import get_logger, get_torch
from level_1 import FiLM, BaseVisionModel

logger = get_logger(__name__)
torch = get_torch()
nn = torch.nn

# DINOv2's recommended input resolution
_DEFAULT_DINOV2_SIZE: Tuple[int, int] = (518, 518)
# Default hidden size for dinov2-base; used only when HF config is unavailable
_DEFAULT_HIDDEN_SIZE: int = 768


class DINOv2Model(BaseVisionModel):
    """
    DINOv2 backbone with configurable fusion and regression head.

    Loads via HuggingFace. Supports single-image and left/right split input
    with either FiLM or cross-gating fusion. For timm-format models use
    TimmModel instead.
    """

    def __init__(
        self,
        model_name: str = 'facebook/dinov2-base',
        pretrained: bool = True,
        num_classes: int = 1,
        input_size: Optional[Tuple[int, int]] = None,
        use_tiles: bool = False,
        tile_grid_size: int = 2,
        use_film: bool = False,
    ):
        """
        Args:
            model_name: HuggingFace model ID or path to local weights.
            pretrained: Load pretrained weights (default: True).
            num_classes: Number of regression outputs (default: 1).
            input_size: Override inferred input size as (height, width).
            use_tiles: Process each half as a tile grid instead of directly.
            tile_grid_size: Grid dimension for tile extraction (e.g. 2 → 2×2).
            use_film: Use FiLM fusion; if False, uses cross-gating.

        Raises:
            ValueError: If arguments fail validation.
            RuntimeError: If the HuggingFace model cannot be loaded.
        """
        super().__init__()

        if not model_name or not isinstance(model_name, str):
            raise ValueError(f"model_name must be a non-empty string, got {model_name!r}")
        if not isinstance(num_classes, int) or num_classes < 1:
            raise ValueError(f"num_classes must be a positive integer, got {num_classes}")
        if input_size is not None:
            if not isinstance(input_size, (tuple, list)) or len(input_size) != 2:
                raise ValueError(f"input_size must be (height, width), got {input_size}")
            h, w = input_size
            if not isinstance(h, int) or not isinstance(w, int) or h < 1 or w < 1:
                raise ValueError(f"input_size dimensions must be positive integers, got {input_size}")

        self.model_name = model_name
        self.num_classes = num_classes
        self.use_tiles = use_tiles
        self.tile_grid_size = tile_grid_size
        self.use_film = use_film
        self._pretrained_loaded: bool = False  # set to True inside _load_backbone on success

        logger.info(f"Creating DINOv2 model: {model_name} (pretrained={pretrained})")
        self._load_backbone(model_name, pretrained)

        if input_size is not None:
            self.input_size = input_size
            logger.debug(f"Input size overridden to: {self.input_size}")

        self._init_heads()

    # ------------------------------------------------------------------
    # Backbone loading
    # ------------------------------------------------------------------

    def _load_hf_model_with_retry(self, model_name: str) -> HFDinov2Model:
        """
        Load a HuggingFace DINOv2 model, retrying once on protobuf AttributeError.

        The MessageFactory.GetPrototype error is a harmless protobuf version
        mismatch that does not prevent the model from loading correctly.
        """
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                return HFDinov2Model.from_pretrained(model_name)
            except AttributeError as e:
                if 'MessageFactory' in str(e) and 'GetPrototype' in str(e):
                    logger.warning("Suppressed MessageFactory.GetPrototype error — retrying")
                    return HFDinov2Model.from_pretrained(model_name)
                raise

    def _load_backbone(self, model_name: str, pretrained: bool) -> None:
        """
        Load the HuggingFace backbone and resolve feat_dim and input_size from its config.
        """
        try:
            logger.info(f"Loading HuggingFace DINOv2 from: {model_name}")
            self.backbone = self._load_hf_model_with_retry(model_name)
            self._pretrained_loaded = True
            logger.info("Successfully loaded HuggingFace DINOv2 model")
        except Exception as e:
            logger.error(f"Failed to load HuggingFace model: {e}")
            raise

        # Resolve feature dimension
        if hasattr(self.backbone, 'config') and hasattr(self.backbone.config, 'hidden_size'):
            hidden_size = self.backbone.config.hidden_size
        else:
            hidden_size = _DEFAULT_HIDDEN_SIZE
            logger.warning(
                f"Could not read hidden_size from HF config — using default {hidden_size}"
            )
        self.feat_dim: int = hidden_size * 3  # CLS + AVG_pool + MAX_pool
        logger.info(f"Feature dim: {hidden_size} → {self.feat_dim} (CLS+AVG+MAX)")

        # Resolve input size
        if hasattr(self.backbone, 'config') and hasattr(self.backbone.config, 'image_size'):
            self.input_size: Tuple[int, int] = (
                self.backbone.config.image_size,
                self.backbone.config.image_size,
            )
            logger.info(f"Input size from HF config: {self.input_size}")
        else:
            self.input_size = _DEFAULT_DINOV2_SIZE
            logger.info(f"Using default DINOv2 input size: {self.input_size}")

        if hasattr(self.backbone, 'gradient_checkpointing_enable'):
            self.backbone.gradient_checkpointing_enable()
            logger.info("Gradient checkpointing enabled")

    # ------------------------------------------------------------------
    # Head and fusion initialisation
    # ------------------------------------------------------------------

    def _init_heads(self) -> None:
        """Create regression heads for single and split input modes."""
        hidden_single = max(32, int(self.feat_dim * 0.25))
        self.head_single = nn.Sequential(
            nn.Linear(self.feat_dim, hidden_single),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(hidden_single, self.num_classes),
        )

        hidden_split = max(32, int(self.feat_dim * 2 * 0.25))
        self.head_split = nn.Sequential(
            nn.Linear(self.feat_dim * 2, hidden_split),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(hidden_split, self.num_classes),
        )

        self._init_fusion_module()

        if self.use_tiles:
            logger.info(
                f"Tile processing enabled: {self.tile_grid_size}×{self.tile_grid_size} grid per half"
            )

    def _init_fusion_module(self) -> None:
        """Create FiLM or cross-gating layers for left/right feature fusion."""
        if self.use_film:
            self.film = FiLM(self.feat_dim)
            logger.info("Using FiLM fusion")
        else:
            self.cross_gate_left = nn.Linear(self.feat_dim, self.feat_dim)
            self.cross_gate_right = nn.Linear(self.feat_dim, self.feat_dim)
            logger.info("Using cross-gating fusion")

    # ------------------------------------------------------------------
    # Feature extraction
    # ------------------------------------------------------------------

    def _extract_hf_features(self, x: torch.Tensor) -> torch.Tensor:
        """
        Extract CLS + average-pooled + max-pooled patch features from the backbone.

        Args:
            x: (B, C, H, W)

        Returns:
            (B, 3*D) — CLS token concatenated with avg and max patch pooling.
        """
        output = self.backbone(x)
        if not hasattr(output, 'last_hidden_state'):
            raise RuntimeError(f"Unexpected HF output format: {type(output)}")

        last_hidden = output.last_hidden_state      # (B, 1+N_patches, D)
        cls_token = last_hidden[:, 0, :]            # (B, D)
        patch_tokens = last_hidden[:, 1:, :]        # (B, N_patches, D)
        avg_pool = patch_tokens.mean(dim=1)          # (B, D)
        max_pool = patch_tokens.max(dim=1)[0]        # (B, D)
        return torch.cat([cls_token, avg_pool, max_pool], dim=1)  # (B, 3*D)

    def _extract_tiles(self, img: torch.Tensor) -> torch.Tensor:
        """
        Slice img into a tile_grid_size × tile_grid_size grid and resize each tile.

        Args:
            img: (B, C, H, W)

        Returns:
            (B * num_tiles, C, H, W) with each tile resized to self.input_size.
        """
        B, C, H, W = img.shape
        tile_h = H // self.tile_grid_size
        tile_w = W // self.tile_grid_size
        tiles = []
        for i in range(self.tile_grid_size):
            for j in range(self.tile_grid_size):
                h_start = i * tile_h
                h_end = (i + 1) * tile_h if i < self.tile_grid_size - 1 else H
                w_start = j * tile_w
                w_end = (j + 1) * tile_w if j < self.tile_grid_size - 1 else W
                tile = img[:, :, h_start:h_end, w_start:w_end]
                if tile.shape[2] != self.input_size[0] or tile.shape[3] != self.input_size[1]:
                    tile = torch.nn.functional.interpolate(
                        tile, size=self.input_size, mode='bilinear', align_corners=False
                    )
                tiles.append(tile)
        return torch.cat(tiles, dim=0)  # (B * num_tiles, C, H, W)

    def _process_tiles(self, img: torch.Tensor) -> torch.Tensor:
        """
        Extract tile features and mean-pool them into a single feature vector per image.

        Args:
            img: (B, C, H, W)

        Returns:
            (B, feat_dim)
        """
        B = img.shape[0]
        num_tiles = self.tile_grid_size * self.tile_grid_size
        tiles = self._extract_tiles(img)                                    # (B*T, C, H, W)
        tile_features = self._extract_hf_features(tiles)                   # (B*T, feat_dim)
        tile_features = tile_features.view(B, num_tiles, self.feat_dim)    # (B, T, feat_dim)
        return tile_features.mean(dim=1)                                    # (B, feat_dim)

    # ------------------------------------------------------------------
    # Forward
    # ------------------------------------------------------------------

    def forward(
        self, x: Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]
    ) -> torch.Tensor:
        """
        Forward pass supporting single-image and left/right split input.

        Args:
            x: Single tensor (B, C, H, W) or tuple of two tensors for split mode.

        Returns:
            (B, num_classes)
        """
        if isinstance(x, tuple):
            left_img, right_img = x
            extractor = self._process_tiles if self.use_tiles else self._extract_hf_features
            left_feat = extractor(left_img)   # (B, feat_dim)
            right_feat = extractor(right_img) # (B, feat_dim)

            if self.use_film:
                context = (left_feat + right_feat) / 2
                gamma, beta = self.film(context)
                left_feat = left_feat * (1 + gamma) + beta
                right_feat = right_feat * (1 + gamma) + beta
            else:
                # Cross-gating: each branch is gated by the opposite branch's features
                g_l = torch.sigmoid(self.cross_gate_left(right_feat))
                g_r = torch.sigmoid(self.cross_gate_right(left_feat))
                left_feat = left_feat * g_l
                right_feat = right_feat * g_r

            combined = torch.cat([left_feat, right_feat], dim=1)  # (B, feat_dim*2)
            return self.head_split(combined)
        else:
            extractor = self._process_tiles if self.use_tiles else self._extract_hf_features
            return self.head_single(extractor(x))

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def get_input_size(self) -> Tuple[int, int]:
        """Return expected input size as (height, width)."""
        return self.input_size

    def freeze_backbone(self) -> None:
        """Freeze all backbone parameters."""
        for param in self.backbone.parameters():
            param.requires_grad = False
        logger.info(f"Backbone frozen: {self.model_name}")

    def unfreeze_backbone(self) -> None:
        """Unfreeze all backbone parameters."""
        for param in self.backbone.parameters():
            param.requires_grad = True
        logger.info(f"Backbone unfrozen: {self.model_name}")

    def is_pretrained(self) -> bool:
        """Return True if pretrained weights were successfully loaded."""
        return self._pretrained_loaded