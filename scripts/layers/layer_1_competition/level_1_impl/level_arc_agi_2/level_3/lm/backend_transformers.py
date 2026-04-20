"""Hugging Face Transformers-backed ARC LM backend with conservative defaults."""

import importlib
from typing import Any

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    ArcLmAdaptationConfig,
)

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3 import (
    ArcLmBackend,
    ArcLmBackendConfig,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3 import (
    SharedTorchLmInference,
)


class TransformersArcLmBackend(SharedTorchLmInference, ArcLmBackend):
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

    def adapt_for_task(
        self,
        task_payload: dict[str, Any],
        budget_expired: callable,
        *,
        adaptation: ArcLmAdaptationConfig | None = None,
    ) -> dict[str, Any]:
        return {"status": "skipped", "reason": "adaptation_not_unsloth_backend", "backend": "transformers"}
