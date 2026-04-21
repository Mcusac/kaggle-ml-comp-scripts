"""PyTorch dtype, checkpoint, and optional dependency probes for LM backends."""

import importlib
from pathlib import Path
from typing import Any

from layers.layer_0_core.level_0 import get_logger

logger = get_logger(__name__)


def unsloth_available() -> bool:
    try:
        importlib.import_module("unsloth")
        importlib.import_module("peft")
        return True
    except Exception:
        return False


def torch_dtype_from_config(torch: Any, dtype_str: str) -> Any:
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


def load_adapter_state_dict(path: str, torch: Any) -> dict[str, Any]:
    """Load a PEFT adapter/state dict from a file or directory (HF PEFT layout)."""
    p = Path(path).expanduser()
    if p.is_dir():
        for name in ("adapter_model.safetensors", "adapter_model.bin", "pytorch_model.bin"):
            cand = p / name
            if cand.is_file():
                return load_adapter_state_dict(str(cand), torch)
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