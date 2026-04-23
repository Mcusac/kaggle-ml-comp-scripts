"""Unsloth FastLanguageModel + PEFT LoRA LM backend."""

import importlib
from typing import Any, Callable

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_0_infra.level_0 import (
    COMMON_PEFT_PARAMS,
    get_peft_model_state_dict,
    load_adapter_state_dict,
    LmAdaptationConfig,
    set_peft_model_state_dict,
    torch_dtype_from_config,
    unsloth_available,
)
from layers.layer_1_competition.level_0_infra.level_3 import LmBackend, LmBackendConfig
from layers.layer_1_competition.level_0_infra.level_3.lm_backend.shared_hooks import SharedTorchLmHooks
from layers.layer_1_competition.level_0_infra.level_3.lm_backend.shared_inference import SharedTorchLmInference

_logger = get_logger(__name__)

TaskAdaptationFn = Callable[
    ...,
    tuple[dict[str, Any], Any],
]


class UnslothLmBackend(SharedTorchLmInference, LmBackend):
    """Unsloth FastLanguageModel + PEFT LoRA loading (reference notebook parity)."""

    def __init__(
        self,
        config: LmBackendConfig,
        *,
        torch_hooks: SharedTorchLmHooks,
        task_adaptation: TaskAdaptationFn | None = None,
    ) -> None:
        self._config = config
        self._torch_lm_hooks = torch_hooks
        self._task_adaptation = task_adaptation
        self._loaded = False
        self._torch = None
        self._model = None
        self._tokenizer = None
        self._default_adapter_state: dict[str, Any] | None = None

    def backend_name(self) -> str:
        return "unsloth"

    def is_available(self) -> bool:
        return unsloth_available()

    def load(self) -> None:
        if not self.is_available():
            raise RuntimeError("unsloth backend requires unsloth, peft, torch (and bitsandbytes for 4-bit).")
        torch = importlib.import_module("torch")
        unsloth = importlib.import_module("unsloth")
        FastLanguageModel = getattr(unsloth, "FastLanguageModel")

        self._torch = torch
        dtype = torch_dtype_from_config(torch, str(self._config.dtype))

        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=str(self._config.model_path).strip(),
            full_finetuning=bool(self._config.full_finetuning),
            load_in_4bit=bool(self._config.load_in_4bit),
            local_files_only=bool(self._config.local_files_only),
            use_gradient_checkpointing=bool(self._config.use_gradient_checkpointing),
            max_seq_length=int(self._config.max_seq_length or 8192),
            dtype=dtype,
            attn_implementation=str(self._config.from_pretrained_attn_implementation or "eager"),
        )

        model = FastLanguageModel.get_peft_model(model, **COMMON_PEFT_PARAMS)
        model.config._attn_implementation = "eager"

        lp = str(self._config.lora_path).strip() if self._config.lora_path else ""
        if lp:
            state = load_adapter_state_dict(lp, torch)
            load_result = set_peft_model_state_dict(
                model,
                state,
                adapter_name="default",
            )
            _logger.info("✅ Loaded LoRA weights from %s (peft load_result=%s)", lp, load_result)

        model = FastLanguageModel.for_inference(model)
        model.config._attn_implementation = "eager"
        model.eval()

        self._model = model
        self._tokenizer = tokenizer
        state = get_peft_model_state_dict(model, adapter_name="default")
        self._default_adapter_state = {k: v.detach().clone() for k, v in state.items()}
        self._loaded = True

    def adapt_for_task(
        self,
        task_payload: dict[str, Any],
        budget_expired: callable,
        *,
        adaptation: LmAdaptationConfig | None = None,
    ) -> dict[str, Any]:
        if not self._loaded or self._model is None or self._tokenizer is None:
            return {"status": "skipped", "reason": "not_loaded", "backend": "unsloth"}
        if self._default_adapter_state is None:
            _logger.warning("⚠️ Unsloth adapt_for_task: missing LoRA snapshot; skipping.")
            return {"status": "skipped", "reason": "no_adapter_snapshot", "backend": "unsloth"}
        if self._task_adaptation is None:
            return {"status": "skipped", "reason": "no_task_adaptation_runner", "backend": "unsloth"}

        cfg = adaptation if adaptation is not None else LmAdaptationConfig(steps=1)

        meta, model = self._task_adaptation(
            model=self._model,
            tokenizer=self._tokenizer,
            default_adapter_state=self._default_adapter_state,
            task_payload=task_payload,
            budget_expired=budget_expired,
            adaptation=cfg,
            max_seq_length=int(self._config.max_seq_length or 8192),
        )
        self._model = model
        return meta

    def restore_base_adapter_after_task(self) -> None:
        if not self._loaded or self._model is None or self._default_adapter_state is None:
            return
        set_peft_model_state_dict(
            self._model,
            self._default_adapter_state,
            adapter_name="default",
        )


__all__ = ["UnslothLmBackend", "TaskAdaptationFn"]
