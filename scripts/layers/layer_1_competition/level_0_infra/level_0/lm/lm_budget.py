"""Runtime budgeting and profile controls for LM workflows.

Copied from ARC-AGI-2 contest implementation for reuse by other LM contests.
"""

import os
import time

from dataclasses import dataclass


@dataclass(frozen=True)
class ArcLmRuntimeProfile:
    """Controls attention/compile/allocator behavior for LM backend."""

    attention_mode: str = "auto"  # auto|eager|sdpa
    disable_compile: bool = False
    allocator_expandable_segments: bool = True
    allocator_max_split_size_mb: int = 0


@dataclass
class ArcLmBudget:
    """Tracks global/task/decode deadlines and stop reasons."""

    global_deadline_ts: float = 0.0
    task_deadline_ts: float = 0.0
    decode_deadline_ts: float = 0.0
    stop_reason: str = ""

    def now(self) -> float:
        return float(time.perf_counter())

    def is_expired(self) -> bool:
        now = self.now()
        if self.global_deadline_ts > 0.0 and now >= self.global_deadline_ts:
            self.stop_reason = "global_deadline"
            return True
        if self.task_deadline_ts > 0.0 and now >= self.task_deadline_ts:
            self.stop_reason = "task_deadline"
            return True
        if self.decode_deadline_ts > 0.0 and now >= self.decode_deadline_ts:
            self.stop_reason = "decode_deadline"
            return True
        return False


def apply_runtime_profile(profile: ArcLmRuntimeProfile) -> None:
    """Apply runtime profile via process env vars."""
    if profile.disable_compile:
        os.environ["TORCH_COMPILE_DISABLE"] = "1"
        os.environ["UNSLOTH_USE_COMPILED"] = "0"
    if profile.allocator_expandable_segments:
        if int(profile.allocator_max_split_size_mb or 0) > 0:
            os.environ["PYTORCH_CUDA_ALLOC_CONF"] = (
                f"expandable_segments:True,max_split_size_mb:{int(profile.allocator_max_split_size_mb)}"
            )
        else:
            os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"


def build_budget(
    *,
    max_runtime_sec: float,
    task_runtime_sec: float = 0.0,
    decode_runtime_sec: float = 0.0,
) -> ArcLmBudget:
    now = float(time.perf_counter())
    return ArcLmBudget(
        global_deadline_ts=(now + float(max_runtime_sec)) if float(max_runtime_sec) > 0.0 else 0.0,
        task_deadline_ts=(now + float(task_runtime_sec)) if float(task_runtime_sec) > 0.0 else 0.0,
        decode_deadline_ts=(now + float(decode_runtime_sec)) if float(decode_runtime_sec) > 0.0 else 0.0,
    )

