"""Hardware and device detection utilities.

Torch is treated as an optional dependency.
This module exposes pure hardware facts — no logging, no policy decisions.
"""

from typing import Dict, List

from layers.layer_0_core.level_0 import get_torch, DeviceError

def is_cuda_available() -> bool:
    """Return True if CUDA is available."""
    torch = get_torch()
    if torch is None:
        return False
    return bool(torch.cuda.is_available())


def get_device_info() -> Dict[str, object]:
    """
    Return hardware information.

    Returns:
        {
            "cuda_available": bool,
            "device_count": int,
            "device_names": List[str],
        }
    """
    torch = get_torch()
    if torch is None or not torch.cuda.is_available():
        return {
            "cuda_available": False,
            "device_count": 0,
            "device_names": [],
        }

    count = torch.cuda.device_count()
    names: List[str] = [
        torch.cuda.get_device_name(i) for i in range(count)
    ]

    return {
        "cuda_available": True,
        "device_count": count,
        "device_names": names,
    }


def get_device(device: str = "auto") -> str:
    """
    Resolve device identifier.

    Always returns a string identifier:
        "cpu"
        "cuda"
        "cuda:0"

    Never returns torch.device (core should not leak torch objects).
    """
    if not isinstance(device, str):
        raise DeviceError(f"device must be str, got {type(device).__name__}")
    if not device or not device.strip():
        raise DeviceError("device cannot be empty")
    
    device = device.strip().lower()
    valid_prefixes = ("auto", "cpu", "cuda")
    if not any(device.startswith(p) for p in valid_prefixes):
        raise DeviceError(
            f"Invalid device '{device}'. Must be one of: "
            f"'auto', 'cpu', 'cuda', 'cuda:0', etc."
        )

    torch = get_torch()

    if device == "auto":
        if torch and torch.cuda.is_available():
            return "cuda"
        return "cpu"

    # Explicit user request
    if device.startswith("cuda"):
        if torch is None or not torch.cuda.is_available():
            return "cpu"
        return device

    return "cpu"
