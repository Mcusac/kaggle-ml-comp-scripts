"""
Contest-specific configuration helper.

Applies domain defaults and policies on top of framework helpers.
"""

from typing import Dict, Optional, Tuple, Union, Any

from layers.layer_0_core.level_0 import get_logger
from layers.layer_0_core.level_2 import ConfigHelper

_logger = get_logger(__name__)


class ContestConfigHelper(ConfigHelper):
    """
    Contest-specific configuration helper.

    Adds defaults and heuristics for this competition.
    """

    DEFAULT_NUM_TARGETS = 3
    DEFAULT_MODEL_NAME = "dinov2_base"

    # ------------------------------------------------------------------
    # Domain extraction
    # ------------------------------------------------------------------

    @staticmethod
    def extract_config_settings(
        config: Union[Any, Dict[str, Any]],
        num_primary_targets: Optional[int],
        model_name: Optional[str],
        image_size: Optional[Tuple[int, int]],
    ) -> tuple[int, str, Optional[Tuple[int, int]]]:

        (
            extracted_num_targets,
            extracted_model_name,
            extracted_image_size,
        ) = super(ContestConfigHelper, ContestConfigHelper).extract_config_settings(
            config,
            num_primary_targets,
            model_name,
            image_size,
        )

        # Apply contest defaults
        if extracted_num_targets is None:
            extracted_num_targets = ContestConfigHelper.DEFAULT_NUM_TARGETS
            _logger.info(
                "Using default num_primary_targets=%d",
                extracted_num_targets,
            )

        if extracted_model_name is None:
            extracted_model_name = ContestConfigHelper.DEFAULT_MODEL_NAME
            _logger.info(
                "Using default model_name=%s",
                extracted_model_name,
            )

        return (
            extracted_num_targets,
            extracted_model_name,
            extracted_image_size,
        )

    # ------------------------------------------------------------------
    # Domain mixed precision policy
    # ------------------------------------------------------------------

    @staticmethod
    def setup_mixed_precision(
        config: Union[Any, Dict[str, Any]],
        model_name: Optional[str],
        device: Any,
    ) -> tuple[bool, Optional[Any]]:

        use_mp, scaler = super(
            ContestConfigHelper,
            ContestConfigHelper,
        ).setup_mixed_precision(
            config,
            model_name,
            device,
        )

        # Contest heuristic: transformers default to FP16
        if (
            not use_mp
            and model_name
            and (
                "dinov2" in model_name.lower()
                or "dinov3" in model_name.lower()
            )
        ):
            _logger.info(
                "Auto-enabled mixed precision for transformer model"
            )

            # Re-run with forced flag
            config = _inject_mp_flag(config)

            return super(
                ContestConfigHelper,
                ContestConfigHelper,
            ).setup_mixed_precision(
                config,
                model_name,
                device,
            )

        return use_mp, scaler


# ----------------------------------------------------------------------
# Internal helpers
# ----------------------------------------------------------------------

def _inject_mp_flag(config: Any) -> Any:
    """
    Ensure training.use_mixed_precision=True in config.

    Works for dict and object configs.
    """

    if isinstance(config, dict):
        config = dict(config)
        config.setdefault("training", {})
        config["training"]["use_mixed_precision"] = True
        return config

    # Object config: best-effort
    try:
        config.training.use_mixed_precision = True
    except Exception:
        pass

    return config
