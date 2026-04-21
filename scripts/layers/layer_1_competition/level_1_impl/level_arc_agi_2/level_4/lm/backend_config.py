"""ARC LM backend factory; protocol types live in competition infra."""

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_0_infra.level_0 import unsloth_available
from layers.layer_1_competition.level_0_infra.level_3 import (
    LmBackend,
    LmBackendConfig,
    MockLmBackend,
)
from layers.layer_1_competition.level_0_infra.level_3.lm_backend.backend_transformers import TransformersLmBackend
from layers.layer_1_competition.level_0_infra.level_4.lm_backends.backend_unsloth import UnslothLmBackend

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_4 import (
    arc_default_torch_lm_hooks,
    run_unsloth_task_adaptation,
)

logger = get_logger(__name__)

ArcLmBackend = LmBackend
ArcLmBackendConfig = LmBackendConfig


def build_arc_lm_backend(config: ArcLmBackendConfig) -> ArcLmBackend:
    """Choose LM backend implementation by convention and availability.

    ``backend="auto"`` prefers Unsloth (reference NVARC path) when importable,
    else Hugging Face ``transformers``.
    """
    hooks = arc_default_torch_lm_hooks()
    path = str(config.model_path or "").strip()
    if path.startswith("mock://"):
        return MockLmBackend(config)

    mode = str(config.backend or "auto").strip().lower()
    if mode not in ("auto", "unsloth", "transformers"):
        logger.warning("Unknown backend=%r; using auto.", mode)
        mode = "auto"

    if mode == "unsloth":
        ub = UnslothLmBackend(config, torch_hooks=hooks, task_adaptation=run_unsloth_task_adaptation)
        if not ub.is_available():
            raise RuntimeError("backend='unsloth' requested but unsloth/peft is not importable.")
        return ub

    if mode == "transformers":
        tf_backend = TransformersLmBackend(config, torch_hooks=hooks)
        if not tf_backend.is_available():
            raise RuntimeError("backend='transformers' requested but torch/transformers is not importable.")
        return tf_backend

    if unsloth_available():
        logger.info("✅ LM backend: Unsloth (FastLanguageModel) for model_path=%s", path)
        return UnslothLmBackend(config, torch_hooks=hooks, task_adaptation=run_unsloth_task_adaptation)

    tf_backend = TransformersLmBackend(config, torch_hooks=hooks)
    if tf_backend.is_available():
        logger.info("ℹ️ LM backend: transformers (Unsloth not available) for model_path=%s", path)
        return tf_backend

    logger.warning("Falling back to mock LM backend because neither Unsloth nor transformers is usable.")
    return MockLmBackend(config)
