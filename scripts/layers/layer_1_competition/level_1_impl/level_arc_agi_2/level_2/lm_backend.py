"""ARC language-model backend abstraction with safe fallbacks."""

import importlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from layers.layer_0_core.level_0 import get_logger

from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_0 import (
    arc_grid_to_text_lines,
    ArcLmAdaptationConfig,
    COMMON_PEFT_PARAMS,
)
from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_1 import (
    ArcQwenGridChatFormatter,
    eval_teacher_forced_neg_sum_logprob,
)

logger = get_logger(__name__)

Grid = list[list[int]]

def _token_id_for_single_text(tokenizer: Any, text: str) -> int:
    """Return a single token id for `text` or raise if it encodes to multiple ids."""
    ids = tokenizer.encode(text, add_special_tokens=False)
    if not isinstance(ids, list) or len(ids) != 1:
        raise ValueError(f"Expected {text!r} to encode to 1 token, got {ids!r}")
    return int(ids[0])


def _resolve_arc_digit_token_ids(tokenizer: Any) -> list[int]:
    """Resolve token ids for digit strings '0'..'9' (must be single-token each)."""
    return [_token_id_for_single_text(tokenizer, str(i)) for i in range(10)]


def _resolve_newline_token_id(tokenizer: Any) -> int:
    """Resolve token id for newline (must be single-token)."""
    return _token_id_for_single_text(tokenizer, "\n")


def _resolve_turbo_eos_id(tokenizer: Any, formatter: ArcQwenGridChatFormatter) -> int:
    """Single token id for assistant segment end (reference ``EOS_ID`` / ``im_end``)."""
    ids = tokenizer.encode(str(formatter.im_end), add_special_tokens=False)
    if not isinstance(ids, list) or len(ids) != 1:
        raise ValueError(
            f"im_end {formatter.im_end!r} must encode to exactly one token for turbo_dfs; got {ids!r}"
        )
    return int(ids[0])


def _resolve_turbo_arc_token_table(
    tokenizer: Any,
    formatter: ArcQwenGridChatFormatter,
) -> tuple[tuple[int, ...], int, int]:
    """Return ``(arc_tokens, pad_id, eos_id)`` for NVARC-style ``turbo_dfs`` branching."""
    digit_ids = tuple(_token_id_for_single_text(tokenizer, str(i)) for i in range(10))
    newline_id = _resolve_newline_token_id(tokenizer)
    eos_id = _resolve_turbo_eos_id(tokenizer, formatter)
    arc_tokens = digit_ids + (newline_id, eos_id)
    pad_id = int(getattr(tokenizer, "pad_token_id", None) or 13)
    return arc_tokens, pad_id, eos_id


def _unsloth_available() -> bool:
    try:
        importlib.import_module("unsloth")
        importlib.import_module("peft")
        return True
    except Exception:
        return False


def _torch_dtype_from_config(torch: Any, dtype_str: str) -> Any:
    s = str(dtype_str or "auto").strip().lower()
    if s in ("auto",):
        return torch.float16
    if s in ("float16", "fp16", "half"):
        return torch.float16
    if s in ("bfloat16", "bf16"):
        return torch.bfloat16
    if s in ("float32", "fp32"):
        return torch.float32
    logger.warning("Unknown dtype=%r; using float16 for Unsloth load.", dtype_str)
    return torch.float16


def _load_adapter_state_dict(path: str, torch: Any) -> dict[str, Any]:
    """Load a PEFT adapter/state dict from a file or directory (HF PEFT layout)."""
    p = Path(path).expanduser()
    if p.is_dir():
        for name in ("adapter_model.safetensors", "adapter_model.bin", "pytorch_model.bin"):
            cand = p / name
            if cand.is_file():
                return _load_adapter_state_dict(str(cand), torch)
        raise FileNotFoundError(f"No adapter_model.* weights found under directory: {path}")
    if not p.is_file():
        raise FileNotFoundError(f"LoRA path is not a file or directory: {path}")
    suf = p.suffix.lower()
    if suf == ".safetensors":
        st = importlib.import_module("safetensors.torch")
        load_file = getattr(st, "load_file")
        return dict(load_file(str(p)))
    try:
        return torch.load(str(p), map_location="cpu", weights_only=True)
    except TypeError:
        return torch.load(str(p), map_location="cpu")


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


class _SharedTorchLmInference:
    """Forward-pass inference shared by Transformers and Unsloth backends (no decoding policy)."""

    _loaded: bool
    _torch: Any
    _model: Any
    _tokenizer: Any

    def get_tokenizer(self) -> Any | None:
        return self._tokenizer

    def turbo_dfs_beams(
        self,
        prefix_token_ids: list[int],
        max_new_tokens: int,
        max_score: float,
        end_time: float,
        *,
        inner_loop_wall_sec: float | None = None,
    ) -> list[tuple[float, list[int]]]:
        """Run ``inference_turbo_dfs`` for batch row 0; returns ``[(beam_nll, token_ids), ...]`` sorted by NLL."""
        if not self._loaded or self._model is None or self._tokenizer is None:
            raise RuntimeError("LM backend not loaded; call load() before turbo_dfs_beams().")

        from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.llm_decoding import (
            REFERENCE_INNER_LOOP_WALL_SEC,
            inference_turbo_dfs,
        )

        fmt = ArcQwenGridChatFormatter(tokenizer=self._tokenizer)
        arc_tokens, pad_id, eos_id = _resolve_turbo_arc_token_table(self._tokenizer, fmt)
        wall = float(inner_loop_wall_sec) if inner_loop_wall_sec is not None else float(REFERENCE_INNER_LOOP_WALL_SEC)
        raw = inference_turbo_dfs(
            self._model,
            prefix_token_ids,
            int(max_new_tokens),
            float(max_score),
            float(end_time),
            inner_loop_wall_sec=wall,
            arc_tokens=arc_tokens,
            pad_id=pad_id,
            eos_id=eos_id,
        )
        for bid, beams in raw:
            if int(bid) == 0:
                return [(float(s), list(toks)) for s, toks in beams]
        return []

    def infer_cell_probs(self, input_grid: Grid) -> list[list[list[float]]]:
        """Infer per-cell digit probabilities from a real LM forward pass.

        Returns an ``[H][W][10]`` list structure aligned with `llm_tta_runner`'s
        prefix indexing (prefix length == cell index). This does not implement
        DFS/beam search yet; it uses a greedy rollout to condition later cells.
        """
        if not self._loaded or self._model is None or self._tokenizer is None or self._torch is None:
            raise RuntimeError("LM backend not loaded; call load() before infer_cell_probs().")

        torch = self._torch
        model = self._model
        tokenizer = self._tokenizer

        h = len(input_grid)
        w = len(input_grid[0]) if h else 0
        if h <= 0 or w <= 0:
            return []

        device = next(model.parameters()).device
        formatter = ArcQwenGridChatFormatter(tokenizer=tokenizer)
        prompt = formatter.fmt_query_from_input_grid(input_grid)
        prompt_ids = tokenizer.encode(prompt, add_special_tokens=False)
        if not isinstance(prompt_ids, list) or not prompt_ids:
            raise RuntimeError("Tokenization produced empty prompt ids.")

        digit_token_ids = _resolve_arc_digit_token_ids(tokenizer)
        newline_token_id = _resolve_newline_token_id(tokenizer)

        out: list[list[list[float]]] = [[[0.0 for _ in range(10)] for _ in range(w)] for _ in range(h)]
        generated_ids: list[int] = []

        with torch.no_grad():
            for r in range(h):
                for c in range(w):
                    input_ids = torch.tensor([prompt_ids + generated_ids], device=device, dtype=torch.long)
                    outputs = model(input_ids=input_ids, return_dict=True, use_cache=False)
                    logits = outputs.logits[0, -1, :]
                    probs = torch.softmax(logits.float(), dim=-1)
                    digit_probs = [float(probs[int(tid)].item()) for tid in digit_token_ids]

                    s = float(sum(digit_probs))
                    if s <= 0.0:
                        digit_probs = [0.1] * 10
                        s = 1.0
                    digit_probs = [float(p / s) for p in digit_probs]
                    out[r][c] = digit_probs

                    best_color = max(range(10), key=lambda i: digit_probs[i])
                    generated_ids.append(int(digit_token_ids[int(best_color)]))
                generated_ids.append(int(newline_token_id))

        return out

    def score_candidate_grid(self, task_payload: dict[str, Any], candidate_grid: Grid) -> float:
        if not self._loaded or self._model is None or self._tokenizer is None:
            return 0.0

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

    def adapt_for_task(
        self,
        task_payload: dict[str, Any],
        budget_expired: callable,
        *,
        adaptation: ArcLmAdaptationConfig | None = None,
    ) -> dict[str, Any]:
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

    def get_tokenizer(self) -> Any | None:
        return None

    def turbo_dfs_beams(
        self,
        prefix_token_ids: list[int],
        max_new_tokens: int,
        max_score: float,
        end_time: float,
        *,
        inner_loop_wall_sec: float | None = None,
    ) -> list[tuple[float, list[int]]]:
        return []


class TransformersArcLmBackend(_SharedTorchLmInference, ArcLmBackend):
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


class UnslothArcLmBackend(_SharedTorchLmInference, ArcLmBackend):
    """Unsloth FastLanguageModel + PEFT LoRA loading (reference notebook parity).

    Mirrors NVARC reference: ``FastLanguageModel.from_pretrained`` with 4-bit,
    ``get_peft_model`` with fixed ``peft_params``, optional ``set_peft_model_state_dict``
    from ``lora_path``, then ``FastLanguageModel.for_inference``.
    """

    def __init__(self, config: ArcLmBackendConfig) -> None:
        self._config = config
        self._loaded = False
        self._torch = None
        self._model = None
        self._tokenizer = None
        self._default_adapter_state: dict[str, Any] | None = None

    def backend_name(self) -> str:
        return "unsloth"

    def is_available(self) -> bool:
        return _unsloth_available()

    def load(self) -> None:
        if not self.is_available():
            raise RuntimeError("unsloth backend requires unsloth, peft, torch (and bitsandbytes for 4-bit).")
        torch = importlib.import_module("torch")
        unsloth = importlib.import_module("unsloth")
        peft = importlib.import_module("peft")
        FastLanguageModel = getattr(unsloth, "FastLanguageModel")
        set_peft_model_state_dict = getattr(peft, "set_peft_model_state_dict")
        get_peft_model_state_dict = getattr(peft, "get_peft_model_state_dict")

        self._torch = torch
        dtype = _torch_dtype_from_config(torch, str(self._config.dtype))

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
            state = _load_adapter_state_dict(lp, torch)
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
        from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.lm_task_adaptation import (
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
        from layers.layer_1_competition.level_1_impl.level_arc_agi_2.level_2.lm_task_adaptation import (
            restore_peft_adapter_baseline,
        )

        self._model = restore_peft_adapter_baseline(self._model, self._default_adapter_state)


def build_lm_backend(config: ArcLmBackendConfig) -> ArcLmBackend:
    """Choose LM backend implementation by convention and availability.

    ``backend="auto"`` prefers Unsloth (reference NVARC path) when importable,
    else Hugging Face ``transformers``.
    """
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
    if _unsloth_available():
        logger.info("✅ LM backend: Unsloth (FastLanguageModel) for model_path=%s", path)
        return UnslothArcLmBackend(config)

    tf_backend = TransformersArcLmBackend(config)
    if tf_backend.is_available():
        logger.info("ℹ️ LM backend: transformers (Unsloth not available) for model_path=%s", path)
        return tf_backend

    logger.warning("Falling back to mock LM backend because neither Unsloth nor transformers is usable.")
    return MockArcLmBackend(config)
