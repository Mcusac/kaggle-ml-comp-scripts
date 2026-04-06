"""ARC language-model backend abstraction with safe fallbacks."""

from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Any

from layers.layer_0_core.level_0 import get_logger

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


class ArcLmBackend:
    """Minimal backend protocol for ARC LM operations."""

    def backend_name(self) -> str:
        raise NotImplementedError

    def is_available(self) -> bool:
        raise NotImplementedError

    def load(self) -> None:
        raise NotImplementedError

    def adapt_for_task(self, task_payload: dict[str, Any], budget_expired: callable) -> dict[str, Any]:
        raise NotImplementedError

    def infer_cell_probs(self, input_grid: Grid) -> list[list[list[float]]]:
        raise NotImplementedError

    def score_candidate_grid(self, task_payload: dict[str, Any], candidate_grid: Grid) -> float:
        raise NotImplementedError


class MockArcLmBackend(ArcLmBackend):
    """Deterministic backend for environments without LM dependencies."""

    def __init__(self, config: ArcLmBackendConfig) -> None:
        self._config = config
        self._loaded = False

    def backend_name(self) -> str:
        return "mock"

    def is_available(self) -> bool:
        return True

    def load(self) -> None:
        self._loaded = True

    def adapt_for_task(self, task_payload: dict[str, Any], budget_expired: callable) -> dict[str, Any]:
        return {"status": "ok", "steps": 0, "backend": "mock"}

    def infer_cell_probs(self, input_grid: Grid) -> list[list[list[float]]]:
        h = len(input_grid)
        w = len(input_grid[0]) if h else 0
        out = [[[1e-4 for _ in range(10)] for _ in range(w)] for _ in range(h)]
        for r in range(h):
            for c in range(w):
                color = int(input_grid[r][c]) % 10
                out[r][c][color] = 0.9
        return out

    def score_candidate_grid(self, task_payload: dict[str, Any], candidate_grid: Grid) -> float:
        train = task_payload.get("train", []) if isinstance(task_payload, dict) else []
        if not isinstance(train, list):
            return 0.0
        score = 0.0
        for pair in train:
            if not isinstance(pair, dict):
                continue
            out = pair.get("output")
            if not isinstance(out, list):
                continue
            same = 0
            total = 0
            for r in range(min(len(out), len(candidate_grid))):
                for c in range(min(len(out[r]), len(candidate_grid[r]))):
                    total += 1
                    if int(out[r][c]) == int(candidate_grid[r][c]):
                        same += 1
            if total > 0:
                score += float(same) / float(total)
        return float(score)


class TransformersArcLmBackend(ArcLmBackend):
    """Transformers-backed backend with conservative optional behavior."""

    def __init__(self, config: ArcLmBackendConfig) -> None:
        self._config = config
        self._loaded = False
        self._transformers = None
        self._torch = None
        self._model = None
        self._tokenizer = None

    def backend_name(self) -> str:
        return "transformers"

    def is_available(self) -> bool:
        try:
            importlib.import_module("transformers")
            importlib.import_module("torch")
            return True
        except Exception:
            return False

    def load(self) -> None:
        if not self.is_available():
            raise RuntimeError("transformers backend requires torch and transformers.")
        self._transformers = importlib.import_module("transformers")
        self._torch = importlib.import_module("torch")
        AutoModelForCausalLM = getattr(self._transformers, "AutoModelForCausalLM")
        AutoTokenizer = getattr(self._transformers, "AutoTokenizer")
        dtype = None
        if str(self._config.dtype).lower() in ("float16", "fp16"):
            dtype = getattr(self._torch, "float16")
        kwargs: dict[str, Any] = {
            "torch_dtype": dtype,
            "trust_remote_code": True,
        }
        if bool(self._config.load_in_4bit):
            kwargs["load_in_4bit"] = True
        self._tokenizer = AutoTokenizer.from_pretrained(self._config.model_path, trust_remote_code=True)
        self._model = AutoModelForCausalLM.from_pretrained(self._config.model_path, **kwargs)
        self._model.eval()
        self._loaded = True

    def adapt_for_task(self, task_payload: dict[str, Any], budget_expired: callable) -> dict[str, Any]:
        # Placeholder: keep deterministic no-op until dedicated adaptation engine runs.
        return {"status": "skipped", "reason": "adaptation_not_configured", "backend": "transformers"}

    def infer_cell_probs(self, input_grid: Grid) -> list[list[list[float]]]:
        # Conservative fallback: infer from input structure if decoding pipeline not yet token-driven.
        h = len(input_grid)
        w = len(input_grid[0]) if h else 0
        out = [[[1e-4 for _ in range(10)] for _ in range(w)] for _ in range(h)]
        for r in range(h):
            for c in range(w):
                out[r][c][int(input_grid[r][c]) % 10] = 0.7
        return out

    def score_candidate_grid(self, task_payload: dict[str, Any], candidate_grid: Grid) -> float:
        if not self._loaded or self._model is None or self._tokenizer is None:
            return 0.0
        try:
            from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1.eval_teacher_forced_score import (
                eval_teacher_forced_neg_sum_logprob,
            )
            from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0.arc_digit_grid_text import (
                arc_grid_to_text_lines,
            )

            device = next(self._model.parameters()).device
            answer = arc_grid_to_text_lines(candidate_grid)
            qtxt = ""
            if getattr(self._tokenizer, "bos_token", None):
                qtxt = str(self._tokenizer.bos_token)
            nll = eval_teacher_forced_neg_sum_logprob(
                model=self._model,
                tokenizer=self._tokenizer,
                query_text=qtxt,
                answer_text=answer,
                device=device,
            )
            if nll is None:
                return 0.0
            return float(-nll)
        except Exception:
            return 0.0


def build_lm_backend(config: ArcLmBackendConfig) -> ArcLmBackend:
    """Choose LM backend implementation by model_path convention and availability."""
    path = str(config.model_path or "").strip()
    if path.startswith("mock://"):
        return MockArcLmBackend(config)
    tf_backend = TransformersArcLmBackend(config)
    if tf_backend.is_available():
        return tf_backend
    logger.warning("Falling back to mock LM backend because transformers dependencies are unavailable.")
    return MockArcLmBackend(config)
