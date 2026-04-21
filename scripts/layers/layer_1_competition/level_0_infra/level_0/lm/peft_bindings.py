"""Lazy ``peft`` bindings for Unsloth / LoRA backends."""

import importlib

from typing import Any


def peft_module() -> Any:
    return importlib.import_module("peft")


def get_peft_model_state_dict(model: Any, adapter_name: str = "default") -> dict[str, Any]:
    peft = peft_module()
    fn = getattr(peft, "get_peft_model_state_dict")
    return fn(model, adapter_name=adapter_name)


def set_peft_model_state_dict(
    model: Any,
    state_dict: dict[str, Any],
    *,
    adapter_name: str = "default",
) -> Any:
    peft = peft_module()
    fn = getattr(peft, "set_peft_model_state_dict")
    return fn(model, state_dict, adapter_name=adapter_name)


__all__ = [
    "get_peft_model_state_dict",
    "peft_module",
    "set_peft_model_state_dict",
]
