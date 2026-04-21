"""LM backend configuration and abstract base for causal LM contest workflows."""

from dataclasses import dataclass
from typing import Any, Literal

from layers.layer_1_competition.level_0_infra.level_0.lm import LmAdaptationConfig

Grid = list[list[int]]


@dataclass(frozen=True)
class LmBackendConfig:
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


class LmBackend:
    """Minimal backend protocol for LM inference and optional per-task adaptation."""

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
        adaptation: LmAdaptationConfig | None = None,
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
        """After inference, reset task-scoped adapter to the loaded snapshot; no-op by default."""
        return