"""Unsloth FastLanguageModel + PEFT LoRA ARC LM backend (reference NVARC parity)."""

import importlib
from typing import Any

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_0_infra.level_0 import (
    load_adapter_state_dict,
    torch_dtype_from_config,
    unsloth_available,
)
from layers.layer_1_competition.level_0_infra.level_3 import LmBackend, LmBackendConfig

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    ArcLmAdaptationConfig,
    COMMON_PEFT_PARAMS,
    get_peft_model_state_dict,
    set_peft_model_state_dict,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_3 import (
    SharedTorchLmInference,
)


logger = get_logger(__name__)


class UnslothArcLmBackend(SharedTorchLmInference, LmBackend):
    """Unsloth FastLanguageModel + PEFT LoRA loading (reference notebook parity).

    Mirrors NVARC reference: ``FastLanguageModel.from_pretrained`` with 4-bit,
    ``get_peft_model`` with fixed ``peft_params``, optional ``set_peft_model_state_dict``
    from ``lora_path``, then ``FastLanguageModel.for_inference``.
    """

    def __init__(self, config: LmBackendConfig) -> None:
        self._config = config
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
            logger.info("✅ Loaded LoRA weights from %s (peft load_result=%s)", lp, load_result)

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
        adaptation: ArcLmAdaptationConfig | None = None,
    ) -> dict[str, Any]:
        if not self._loaded or self._model is None or self._tokenizer is None:
            return {"status": "skipped", "reason": "not_loaded", "backend": "unsloth"}
        if self._default_adapter_state is None:
            logger.warning("⚠️ Unsloth adapt_for_task: missing LoRA snapshot; skipping.")
            return {"status": "skipped", "reason": "no_adapter_snapshot", "backend": "unsloth"}
        cfg = adaptation if adaptation is not None else ArcLmAdaptationConfig(steps=1)
        from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_4.lm_task_adaptation import (
            run_unsloth_task_adaptation,
        )

        meta, model = run_unsloth_task_adaptation(
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
