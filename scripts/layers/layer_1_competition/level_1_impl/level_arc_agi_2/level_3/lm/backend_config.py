"""ARC LM backend config + ABC + factory selector."""

from dataclasses import dataclass
from typing import Any, Literal

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    ArcLmAdaptationConfig,
)

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3 import (
    unsloth_available,
)

logger = get_logger(__name__)

Grid = list[list[int]]


@dataclass(frozen=True)
class ArcLmBackendConfig:
    model_path: str
    lora_path: str | None = None
    dtype: str = "auto"
    load_in_4bit: bool = True
    attention_mode: str = "auto"
    disable_compile: bool = False
    device: str = "auto"
    seed: int = 0
    backend: Literal["auto", "unsloth", "transformers"] = "auto"
    max_seq_length: int = 8192
    local_files_only: bool = False
    full_finetuning: bool = False
    use_gradient_checkpointing: bool = False
    from_pretrained_attn_implementation: str = "eager"


class ArcLmBackend:
    """Minimal backend protocol for ARC LM operations."""

    def backend_name(self) -> str:
        raise NotImplementedError

    def is_available(self) -> bool:
        raise NotImplementedError

    def load(self) -> None:
        raise NotImplementedError

    def adapt_for_task(
        self,
        task_payload: dict[str, Any],
        budget_expired: callable,
        *,
        adaptation: ArcLmAdaptationConfig | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError

    def infer_cell_probs(self, input_grid: Grid) -> list[list[list[float]]]:
        raise NotImplementedError

    def score_candidate_grid(self, task_payload: dict[str, Any], candidate_grid: Grid) -> float:
        raise NotImplementedError

    def get_tokenizer(self) -> Any | None:
        raise NotImplementedError

    def turbo_dfs_beams(
        self,
        prefix_token_ids: list[int],
        max_new_tokens: int,
        max_score: float,
        end_time: float,
        *,
        inner_loop_wall_sec: float | None = None,
    ) -> list[tuple[float, list[int]]]:
        raise NotImplementedError

    def restore_base_adapter_after_task(self) -> None:
        """After inference, reset task-scoped LoRA to the loaded snapshot (Unsloth); no-op by default."""
        return


def build_lm_backend(config: ArcLmBackendConfig) -> ArcLmBackend:
    """Choose LM backend implementation by convention and availability.

    ``backend="auto"`` prefers Unsloth (reference NVARC path) when importable,
    else Hugging Face ``transformers``.
    """
    # Lazy imports to avoid circularity: concrete backends inherit from
    # ``ArcLmBackend`` defined in this module.
    from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3.lm.backend_mock import (
        MockArcLmBackend,
    )
    from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3.lm.backend_transformers import (
        TransformersArcLmBackend,
    )
    from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_4.lm.backend_unsloth import (
        UnslothArcLmBackend,
    )

    path = str(config.model_path or "").strip()
    if path.startswith("mock://"):
        return MockArcLmBackend(config)

    mode = str(config.backend or "auto").strip().lower()
    if mode not in ("auto", "unsloth", "transformers"):
        logger.warning("Unknown backend=%r; using auto.", mode)
        mode = "auto"

    if mode == "unsloth":
        ub = UnslothArcLmBackend(config)
        if not ub.is_available():
            raise RuntimeError("backend='unsloth' requested but unsloth/peft is not importable.")
        return ub

    if mode == "transformers":
        tf_backend = TransformersArcLmBackend(config)
        if not tf_backend.is_available():
            raise RuntimeError("backend='transformers' requested but torch/transformers is not importable.")
        return tf_backend

    # auto
    if unsloth_available():
        logger.info("✅ LM backend: Unsloth (FastLanguageModel) for model_path=%s", path)
        return UnslothArcLmBackend(config)

    tf_backend = TransformersArcLmBackend(config)
    if tf_backend.is_available():
        logger.info("ℹ️ LM backend: transformers (Unsloth not available) for model_path=%s", path)
        return tf_backend

    logger.warning("Falling back to mock LM backend because neither Unsloth nor transformers is usable.")
    return MockArcLmBackend(config)
